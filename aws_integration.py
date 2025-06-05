import boto3
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class AWSJournalBackup:
    """Handles AWS S3 backup for journal entries"""
    
    def __init__(self, bucket_name=None, region='us-east-1'):
        self.bucket_name = bucket_name or os.environ.get('S3_BACKUP_BUCKET')
        self.region = region
        
        if self.bucket_name:
            self.s3_client = boto3.client('s3', region_name=self.region)
            self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    logger.info(f"Created S3 bucket: {self.bucket_name}")
                    
                    # Enable versioning for backup safety
                    self.s3_client.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
    
    def backup_entries(self, entries):
        """Backup journal entries to S3"""
        if not self.bucket_name:
            logger.warning("No S3 bucket configured for backup")
            return False
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            key = f"journal_backups/journal_entries_{timestamp}.json"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(entries, indent=2),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )
            
            # Also update the 'latest' backup
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key='journal_backups/latest.json',
                Body=json.dumps(entries, indent=2),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Successfully backed up {len(entries)} entries to S3")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to backup to S3: {e}")
            return False
    
    def restore_from_backup(self):
        """Restore journal entries from S3 backup"""
        if not self.bucket_name:
            return None
            
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key='journal_backups/latest.json'
            )
            entries = json.loads(response['Body'].read())
            logger.info(f"Restored {len(entries)} entries from S3 backup")
            return entries
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.info("No backup found in S3")
            else:
                logger.error(f"Failed to restore from S3: {e}")
            return None


class DynamoDBJournalStore:
    """Alternative storage backend using DynamoDB"""
    
    def __init__(self, table_name=None, region='us-east-1'):
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE_NAME', 'gvisit-journal-entries')
        self.region = region
        
        if self.table_name:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
            self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            self.table = self.dynamodb.Table(self.table_name)
            self.table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                try:
                    self.table = self.dynamodb.create_table(
                        TableName=self.table_name,
                        KeySchema=[
                            {'AttributeName': 'id', 'KeyType': 'HASH'}
                        ],
                        AttributeDefinitions=[
                            {'AttributeName': 'id', 'AttributeType': 'N'}
                        ],
                        BillingMode='PAY_PER_REQUEST'
                    )
                    self.table.wait_until_exists()
                    logger.info(f"Created DynamoDB table: {self.table_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create table: {create_error}")
                    raise
    
    def add_entry(self, entry):
        """Add a journal entry to DynamoDB"""
        try:
            self.table.put_item(Item=entry)
            logger.info(f"Added entry {entry['id']} to DynamoDB")
            return True
        except ClientError as e:
            logger.error(f"Failed to add entry to DynamoDB: {e}")
            return False
    
    def get_all_entries(self):
        """Retrieve all journal entries from DynamoDB"""
        try:
            response = self.table.scan()
            entries = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                entries.extend(response.get('Items', []))
            
            # Sort by ID
            entries.sort(key=lambda x: int(x.get('id', 0)))
            
            logger.info(f"Retrieved {len(entries)} entries from DynamoDB")
            return entries
            
        except ClientError as e:
            logger.error(f"Failed to retrieve entries from DynamoDB: {e}")
            return []
    
    def delete_entry(self, entry_id):
        """Delete a journal entry from DynamoDB"""
        try:
            self.table.delete_item(Key={'id': entry_id})
            logger.info(f"Deleted entry {entry_id} from DynamoDB")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete entry from DynamoDB: {e}")
            return False


# Utility function to check AWS credentials
def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"AWS credentials valid. Account: {identity['Account']}")
        return True
    except Exception as e:
        logger.warning(f"AWS credentials not configured or invalid: {e}")
        return False 
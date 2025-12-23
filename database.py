import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from config import config

logger = logging.getLogger(__name__)

class JSONDatabase:
    """JSON-based database for storing bot metadata"""
    
    def __init__(self, db_file: str = None):
        self.db_file = db_file or config.DATABASE_FILE
        self.db_path = Path(self.db_file)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists with proper structure"""
        if not self.db_path.exists():
            initial_data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                "bots": {}
            }
            self._write_db(initial_data)
            logger.info(f"Database created: {self.db_file}")
    
    def _read_db(self) -> Dict[str, Any]:
        """Read entire database"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Database file corrupted: {self.db_file}")
            return {"metadata": {}, "bots": {}}
        except Exception as e:
            logger.error(f"Error reading database: {e}")
            return {"metadata": {}, "bots": {}}
    
    def _write_db(self, data: Dict[str, Any]):
        """Write entire database"""
        try:
            # Update metadata
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["updated_at"] = datetime.now().isoformat()
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing to database: {e}")
    
    def add_bot(self, bot_id: str, bot_data: Dict[str, Any]) -> bool:
        """Add new bot to database"""
        try:
            db = self._read_db()
            
            # Add timestamp
            bot_data["created_at"] = datetime.now().isoformat()
            bot_data["updated_at"] = datetime.now().isoformat()
            
            db["bots"][bot_id] = bot_data
            self._write_db(db)
            logger.info(f"Bot added to database: {bot_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding bot: {e}")
            return False
    
    def get_bot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get bot data by ID"""
        try:
            db = self._read_db()
            return db["bots"].get(bot_id)
        except Exception as e:
            logger.error(f"Error getting bot: {e}")
            return None
    
    def get_all_bots(self) -> Dict[str, Dict[str, Any]]:
        """Get all bots"""
        try:
            db = self._read_db()
            return db.get("bots", {})
        except Exception as e:
            logger.error(f"Error getting all bots: {e}")
            return {}
    
    def update_bot(self, bot_id: str, bot_data: Dict[str, Any]) -> bool:
        """Update existing bot data"""
        try:
            db = self._read_db()
            
            if bot_id not in db["bots"]:
                logger.warning(f"Bot not found: {bot_id}")
                return False
            
            # Preserve creation time, update modification time
            if "created_at" not in bot_data:
                bot_data["created_at"] = db["bots"][bot_id].get("created_at")
            
            bot_data["updated_at"] = datetime.now().isoformat()
            db["bots"][bot_id] = bot_data
            self._write_db(db)
            logger.info(f"Bot updated: {bot_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating bot: {e}")
            return False
    
    def delete_bot(self, bot_id: str) -> bool:
        """Delete bot from database"""
        try:
            db = self._read_db()
            
            if bot_id not in db["bots"]:
                logger.warning(f"Bot not found: {bot_id}")
                return False
            
            del db["bots"][bot_id]
            self._write_db(db)
            logger.info(f"Bot deleted: {bot_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting bot: {e}")
            return False
    
    def get_bots_by_status(self, status: str) -> Dict[str, Dict[str, Any]]:
        """Get all bots with specific status"""
        try:
            all_bots = self.get_all_bots()
            return {bot_id: bot for bot_id, bot in all_bots.items() if bot.get("status") == status}
        except Exception as e:
            logger.error(f"Error filtering bots by status: {e}")
            return {}
    
    def get_bots_by_user(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        """Get all bots created by specific user"""
        try:
            all_bots = self.get_all_bots()
            return {bot_id: bot for bot_id, bot in all_bots.items() if bot.get("user_id") == user_id}
        except Exception as e:
            logger.error(f"Error filtering bots by user: {e}")
            return {}
    
    def bot_exists(self, bot_id: str) -> bool:
        """Check if bot exists in database"""
        try:
            db = self._read_db()
            return bot_id in db["bots"]
        except Exception as e:
            logger.error(f"Error checking bot existence: {e}")
            return False
    
    def get_total_bots(self) -> int:
        """Get total number of bots"""
        try:
            return len(self.get_all_bots())
        except Exception as e:
            logger.error(f"Error getting total bots: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            all_bots = self.get_all_bots()
            statuses = {}
            for bot in all_bots.values():
                status = bot.get("status", "unknown")
                statuses[status] = statuses.get(status, 0) + 1
            
            return {
                "total_bots": len(all_bots),
                "bots_by_status": statuses,
                "database_file": str(self.db_path),
                "database_size_bytes": self.db_path.stat().st_size if self.db_path.exists() else 0
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def export_bots(self, export_file: str) -> bool:
        """Export all bots to file"""
        try:
            db = self._read_db()
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            logger.info(f"Bots exported to: {export_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting bots: {e}")
            return False
    
    def import_bots(self, import_file: str) -> bool:
        """Import bots from file"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            db = self._read_db()
            if "bots" in imported_data:
                db["bots"].update(imported_data["bots"])
                self._write_db(db)
                logger.info(f"Bots imported from: {import_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error importing bots: {e}")
            return False
    
    def backup_database(self, backup_file: str = None) -> bool:
        """Create backup of database"""
        try:
            if backup_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"bots_database_backup_{timestamp}.json"
            
            return self.export_bots(backup_file)
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False

# Global database instance
db = JSONDatabase()

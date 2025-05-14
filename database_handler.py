import os
import sys
import json
import shutil
import time
from pathlib import Path
import logging

class DatabaseHandler:
    def __init__(self, settings_manager=None):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # File paths
        self.db_filename = "transaction_data.json"
        self.config_filename = "config.json"
        self.db_path = self._get_database_path()
        self.config_path = self._get_config_path()

        self.settings_manager = settings_manager

        self._ensure_database_exists()

    def _get_database_path(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            data_dir = os.path.join(base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            return os.path.join(data_dir, self.db_filename)
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), self.db_filename)

    def _get_config_path(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            return os.path.join(base_dir, self.config_filename)
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), self.config_filename)

    def _ensure_database_exists(self):
        if not os.path.exists(self.db_path):
            self.logger.info(f"Creating new database at {self.db_path}")
            self.save_data([])

    def load_data(self):
        try:
            with open(self.db_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.logger.debug(f"Loaded {len(data)} records from database")
                return data
        except FileNotFoundError:
            self.logger.warning(f"Database file not found at {self.db_path}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Database corruption detected: {str(e)}")
            self._backup_corrupted_file()
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error loading database: {str(e)}")
            return []

    def save_data(self, data):
        try:
            if not isinstance(data, list):
                data = [data]

            # Retrieve username from config
            username = self.get_setting('username')

            # Modify each record to include username if it exists
            for record in data:
                if username and 'username' not in record:
                    record['username'] = username
                    self.logger.info(f"Added username '{username}' to transaction")

            # Save the transaction data
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            self.logger.info(f"Saved {len(data)} records to database")
            return True

        except Exception as e:
            self.logger.error(f"Error saving database: {str(e)}")
            return False

    def get_next_id(self):
        data = self.load_data()
        if not data:
            return 1
        max_id = max((record.get('id', 0) for record in data), default=0)
        return max_id + 1

    def record_login_time(self, username):
        try:
            current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")

            # Simpan ke config.json
            login_data = {
                "username": username,
                "login_datetime": current_datetime
            }
            self.save_settings({"last_login": login_data})

            # Hapus hanya pengaturan yang tidak diperlukan
            self.remove_settings(["server", "port", "use_ssl", "mode", "timeout", "auto_sync"])

            self.logger.info(f"User {username} logged in at {current_datetime}")
            return True
        except Exception as e:
            self.logger.error(f"Error recording login time: {str(e)}")
            return False

    def record_logout_time(self):
        try:
            current_time = time.strftime("%H:%M:%S")
            current_date = time.strftime("%Y-%m-%d")

            # Log the logout information instead of saving to config
            self.logger.info(f"User logged out at {current_time} on {current_date}")

            return True
        except Exception as e:
            self.logger.error(f"Error recording logout time: {str(e)}")
            return False

    def get_login_history(self):
        return self.get_setting("login_history", [])

    def get_current_session(self):
        return self.get_setting("current_session")

    def _backup_corrupted_file(self):
        if os.path.exists(self.db_path):
            backup_path = f"{self.db_path}.corrupt.{int(time.time())}"
            shutil.copy2(self.db_path, backup_path)
            self.logger.warning(f"Created backup of corrupted database: {backup_path}")

    def get_settings(self):
        try:
            if self.settings_manager:
                settings = self.settings_manager.get_settings()
                if not settings.get("comcode") or not settings.get("bacode"):
                    self.logger.warning("comcode or bacode missing in settings_manager!")
                return settings

            if os.path.exists(self.config_path):
                self.logger.info(f"Loading config from {self.config_path}")
                with open(self.config_path, 'r', encoding='utf-8') as config_file:
                    settings = json.load(config_file)
                    if not settings.get("comcode") or not settings.get("bacode"):
                        self.logger.warning("comcode or bacode missing in config file!")
                    return settings

            self.logger.error(f"Config file not found at {self.config_path}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            return {}

    def get_setting(self, key, default=None):
        settings = self.get_settings()
        return settings.get(key, default)

    def save_setting(self, key, value):
        try:
            settings = self.get_settings()
            settings[key] = value

            with open(self.config_path, 'w', encoding='utf-8') as config_file:
                json.dump(settings, config_file, indent=4)

            self.logger.info(f"Saved setting: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving setting {key}: {str(e)}")
            return False

    def save_settings(self, settings_dict):
        try:
            current_settings = self.get_settings()
            current_settings.update(settings_dict)

            with open(self.config_path, 'w', encoding='utf-8') as config_file:
                json.dump(current_settings, config_file, indent=4)

            self.logger.info(f"Saved {len(settings_dict)} settings")
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            return False

    def should_embed_settings(self):
        return True

    def get_embedding_keys(self):
        settings = self.get_settings()
        if not settings:
            return ["comcode", "bacode", "username"]

        # Ensure 'username' is always included in embedding keys
        keys = list(settings.keys())
        if 'username' not in keys:
            keys.append('username')
        return keys

    def extract_settings_from_transaction(self, transaction_id=None):
        data = self.load_data()

        if not data:
            self.logger.warning("No transactions found to extract settings from")
            return {}

        if transaction_id is not None:
            transaction = next((t for t in data if t.get('id') == transaction_id), None)
            if not transaction:
                self.logger.warning(f"Transaction with ID {transaction_id} not found")
                return {}
        else:
            transaction = data[-1]

        extracted_settings = {}
        embedding_keys = self.get_embedding_keys()
        for key in embedding_keys:
            if key in transaction:
                extracted_settings[key] = transaction[key]

        return extracted_settings

    def restore_settings_from_latest_transaction(self):
        settings = self.extract_settings_from_transaction()

        if settings:
            success = self.save_settings(settings)
            if success:
                self.logger.info("Settings restored from latest transaction")
            return success
        else:
            self.logger.warning("No settings found in transactions to restore")
            return False

    def get_transaction_by_id(self, transaction_id):
        try:
            data = self.load_data()
            transaction = next((t for t in data if t.get('id') == transaction_id), None)
            return transaction
        except Exception as e:
            self.logger.error(f"Error retrieving transaction with ID {transaction_id}: {str(e)}")
            return None

    def backup_database(self, backup_dir=None):
        try:
            if not backup_dir:
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                backup_dir = os.path.join(base_dir, 'backups')

            os.makedirs(backup_dir, exist_ok=True)

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup_filename = f"transaction_data-{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)

            shutil.copy2(self.db_path, backup_path)

            self.logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creating database backup: {str(e)}")
            return None
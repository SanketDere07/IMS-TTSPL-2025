import io
import os
import glob
from datetime import timedelta
from django.utils import timezone
from django.db import connection
from apscheduler.schedulers.background import BackgroundScheduler
from TTSPL_IMS_App.models import ScheduledBackup,ScheduledBackupDetails
from datetime import datetime 
import shutil


def get_next_file_number(operation, prefix, backup_dir, extension):
    """
    Helper function to generate the next file number for backup files
    by checking existing files in the backup directory.
    """
    file_list = [f for f in os.listdir(backup_dir) if f.startswith(prefix) and f.endswith(extension)]
    numbers = [
        int(f.split('_')[1].split('.')[0]) for f in file_list if f.split('_')[1].isdigit()
    ]
    return max(numbers, default=0) + 1

   
def backup_tables():
    """
    Backs up tables based on ScheduledBackup model entries with operation types:
    - 'backup': Backs up data only.
    - 'cleanup': Clears data after creating a backup file.
    - 'backup_cleanup': Backs up data and then clears it.
    - 'never': Skip backup operation for this entry.

    If a scheduled backup is missed (i.e., next_backup is in the past), 
    generate a backup and update the next_backup date based on backup_interval_days.
    """
    current_date = timezone.now().date()
    current_datetime = timezone.localtime(timezone.now())
    print(f"Current date (in local timezone): {current_date}")
    print(f"Current datetime (in local timezone): {current_datetime}")

    backups = ScheduledBackup.objects.filter(next_backup__date__lte=current_date)

    if not backups:
        print(f"No tables scheduled for backup on {current_date}.")
        return

    # Default desktop path
    default_desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')

    # OneDrive desktop path
    onedrive_desktop = os.path.join(os.environ.get('ONEDRIVE', ''), 'Desktop')

    # Use OneDrive desktop if it exists, otherwise use default
    desktop_path = onedrive_desktop if os.path.exists(onedrive_desktop) else default_desktop

    # Define the backup directory on the desktop
    desktop_backup_dir = os.path.join(desktop_path, 'backups')
    os.makedirs(desktop_backup_dir, exist_ok=True)

    # Define the backup directory relative to the script's location
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    print(f"Desktop backup folder created at: {desktop_backup_dir}")
    print(f"Script backup folder created at: {backup_dir}")

    operations = {"backup": [], "cleanup": [], "backup_cleanup": [], "never": []}

    for backup in backups:
        operations[backup.operation].append(backup)

    for operation, backup_entries in operations.items():
        if not backup_entries:
            continue

        if operation == 'never':
            print("Operation 'never' detected. Skipping backup for these tables.")
            continue

        sql_file_number = get_next_file_number(operation, f"{operation}_", backup_dir, ".sql")
        desktop_sql_file_number = get_next_file_number(operation, f"{operation}_", desktop_backup_dir, ".sql")

        txt_file_number = get_next_file_number(operation, f"{operation}_summary_", backup_dir, ".txt")
        desktop_txt_file_number = get_next_file_number(operation, f"{operation}_summary_", desktop_backup_dir, ".txt")

        all_table_names = []
        cleared_tables = []
        operation_type = operation

        to_date = timezone.now()

        # File paths for script directory
        file_name = f"{operation}_{sql_file_number}_{to_date.strftime('%Y-%m-%d_%H%M%S')}.sql"
        file_path = os.path.join(backup_dir, file_name)

        # File paths for desktop directory
        desktop_file_name = f"{operation}_{desktop_sql_file_number}_{to_date.strftime('%Y-%m-%d_%H%M%S')}.sql"
        desktop_file_path = os.path.join(desktop_backup_dir, desktop_file_name)

        with open(file_path, 'w') as backup_file, open(desktop_file_path, 'w') as desktop_backup_file:
            for backup in backup_entries:
                table_name = backup.table_name

                # Set from_date as last_backup if it exists, otherwise use current_date
                from_date = backup.last_backup.date() if backup.last_backup else current_date

                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
                    columns = [col[0] for col in cursor.fetchall()]
                    columns_str = ", ".join(columns)

                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()

                    backup_file.write(f"-- Data from table {table_name}\n")
                    backup_file.write(f"INSERT INTO {table_name} ({columns_str}) VALUES\n")

                    desktop_backup_file.write(f"-- Data from table {table_name}\n")
                    desktop_backup_file.write(f"INSERT INTO {table_name} ({columns_str}) VALUES\n")

                    row_strs = [
                        "(" + ", ".join(
                            "NULL" if x is None else f"'{x.isoformat()}'" if isinstance(x, datetime) else repr(x)
                            for x in row
                        ) + ")"
                        for row in rows
                    ]
                    backup_file.write(",\n".join(row_strs) + ";\n")
                    desktop_backup_file.write(",\n".join(row_strs) + ";\n")

                    all_table_names.append(table_name)

                    if operation in ["cleanup", "backup_cleanup"]:
                        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
                        cleared_tables.append(table_name)
                        print(f"Data cleared from table: {table_name}")

                    backup.next_backup = current_date + timedelta(days=backup.backup_interval_days)
                    backup.last_backup = timezone.now()
                    backup.save()
                    print(f"Next backup for {table_name} scheduled on {backup.next_backup}.")
                    print(f"Last backup date for {table_name} updated to {backup.last_backup}.")

        file_size = os.path.getsize(file_path) / (1024 * 1024)
        print(f"Combined {operation} saved to {file_path}. Size: {file_size:.2f} MB.")
        print(f"Combined {operation} saved to {desktop_file_path}. Size: {file_size:.2f} MB.")

        # Save summary for both directories
        summary_txt_file_name = f"{operation}_summary_{to_date.strftime('%Y-%m-%d_%H%M%S')}.txt"
        summary_txt_file_path = os.path.join(backup_dir, summary_txt_file_name)

        desktop_summary_txt_file_name = f"{operation}_summary_{to_date.strftime('%Y-%m-%d_%H%M%S')}.txt"
        desktop_summary_txt_file_path = os.path.join(desktop_backup_dir, desktop_summary_txt_file_name)

        with open(summary_txt_file_path, 'w') as summary_file, open(desktop_summary_txt_file_path, 'w') as desktop_summary_file:
            summary_content = (
                f"From Date: {from_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"To Date: {to_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Operation(s): {operation_type}\n"
                f"Backup Tables: {', '.join(all_table_names)}\n"
                f"Backup File Size: {file_size:.2f} MB\n"
                f"Cleared Tables: {', '.join(cleared_tables) if cleared_tables else 'None'}\n"
            )
            summary_file.write(summary_content)
            desktop_summary_file.write(summary_content)

        print(f"Details saved to {summary_txt_file_path}")
        print(f"Details saved to {desktop_summary_txt_file_path}")

        backup_name = f"{file_name}, {summary_txt_file_name}"
        ScheduledBackupDetails.objects.create(
            backup_name=backup_name,
            sql_file_name=file_name,
            txt_file_name=summary_txt_file_name,
            from_date=from_date,
            to_date=to_date,
            scheduled_operation=operation_type,
            file_size=file_size
        )
        print(f"Backup details saved in the database for {backup_name}.")


def start_scheduler():
    """
    Starts the APScheduler scheduler to run backup_tables every 20 seconds.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        backup_tables,
        'interval',
        seconds=20,
        id='backup_tables',
        name='Periodic backup every 20 seconds',
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started for backup operation.")
    print("Scheduled jobs:", scheduler.get_jobs())




    


import sys
import os

#for using fun from another packege
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
# ---------------------------------------------

from ConfigLoader import ConfigLoader


def run_test():
    print("=== Starting ConfigLoader Test (From 'tests' package) ===")

    # שם הקובץ הזמני שייווצר בתוך תיקיית הטסטים
    test_filename = "temp_test_config.txt"

    # תוכן הקובץ המדומה
    file_content = """
message: "c:/users/data/final_project.pdf"
maximum_msg_size: 2048
window_size: 5
timeout: 10
dynamic message size: True
    """

    # 1. יצירת הקובץ
    with open(test_filename, "w") as f:
        f.write(file_content)
    print(f"[V] Created temporary file: {test_filename}")

    # 2. בדיקה שהמערכת טוענת אותו
    try:
        # שימי לב: אנחנו שולחים את שם הקובץ (הוא נמצא באותה תיקייה של הטסט כרגע)
        config = ConfigLoader.load_config(test_filename)
        print(f"[V] Loaded config: {config}")
    except Exception as e:
        print(f"[X] CRITICAL ERROR: {e}")
        return

    # 3. בדיקת הערכים (Assertions)
    errors = []

    if config["message"] != "c:/users/data/final_project.pdf":
        errors.append(f"Bad message: {config['message']}")

    if config["maximum_msg_size"] != 2048:
        errors.append(f"Bad max size: {config['maximum_msg_size']}")

    if config["dynamic message size"] is not True:
        errors.append("Bad dynamic size (should be True)")

    # 4. סיכום
    if not errors:
        print("\n✅ TEST PASSED: All validations correct!")
    else:
        print("\n❌ TEST FAILED:")
        for err in errors:
            print(f" - {err}")

    # 5. ניקוי (מחיקת הקובץ שיצרנו)
    if os.path.exists(test_filename):
        os.remove(test_filename)
        print("[V] Cleaned up temporary file.")


if __name__ == "__main__":
    run_test()
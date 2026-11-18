"""
main.py - run the whole Personal Expense Tracker pipeline.

    python main.py                      # use data/expenses.csv (creates it if missing)
    python main.py --regenerate         # create fresh synthetic data first
    python main.py --csv my_file.csv    # analyse your own CSV
"""
import argparse

from src import config, data_generator, data_loader, report, visualize


def main():
    parser = argparse.ArgumentParser(description="Personal Expense Tracker")
    parser.add_argument("--csv", default=None, help="path to an expenses CSV file")
    parser.add_argument("--regenerate", action="store_true",
                        help="create a fresh synthetic dataset first")
    args = parser.parse_args()

    csv_path = config.BASE_DIR / args.csv if args.csv else config.DEFAULT_CSV

    print("STEP 1/5  Preparing data")
    if args.regenerate or not csv_path.exists():
        data_generator.create_sample_csv(csv_path)
        print(f"          synthetic dataset created: {csv_path.name}")
    else:
        print(f"          using existing file: {csv_path.name}")

    print("STEP 2/5  Loading and cleaning")
    df, log = data_loader.load_expenses(csv_path)
    for key, value in log.items():
        print(f"          {key.replace('_', ' '):<30}: {value}")

    print("STEP 3/5  Saving summary tables")
    for path in report.save_tables(df):
        print(f"          saved {path.relative_to(config.BASE_DIR)}")

    print("STEP 4/5  Drawing charts")
    for path in visualize.save_all_charts(df):
        print(f"          saved {path.relative_to(config.BASE_DIR)}")

    print("STEP 5/5  Writing the text report")
    report_path = report.save_text_report(df, log)
    print(f"          saved {report_path.relative_to(config.BASE_DIR)}\n")
    print(report.build_text_report(df, log))


if __name__ == "__main__":
    main()

from tabulate import tabulate


def df_print(df):
    # Sample N rows
    try:
        sample = df.iloc[:, :7].sample(n=5, random_state=1).reset_index(drop=True)
    except ValueError:
        sample = df
    # Construct headers with dtype shown below each column name
    headers = [
        f"{col}\n({str(dtype)})" for col, dtype in sample.dtypes.items()
    ]

    # Print using tabulate
    print(
        tabulate(
            sample, headers=headers, tablefmt="psql", showindex=False, 
        )
    )

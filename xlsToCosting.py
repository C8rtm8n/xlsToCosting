import streamlit as st
import pandas as pd
import sqlite3
import os

# Funkce pro nahrání dat do SQLite databáze
def upload_data_to_sqlite(excel_data, sqlite_file_path, table_name):
    # Připojení k SQLite databázi
    connection = sqlite3.connect(sqlite_file_path)
    cursor = connection.cursor()

    # Kontrola, zda tabulka existuje
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    table_exists = cursor.fetchone() is not None

    # Pokud tabulka neexistuje, vytvoř ji
    if not table_exists:
        cursor.execute(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {', '.join(f"[{col}] {dtype}" for col, dtype in zip(excel_data.columns, ['INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'TEXT']))}
            );
        """)

    # Vložení dat (bez sloupce 'id', který je AUTOINCREMENT)
    columns_to_insert = [col for col in excel_data.columns]
    data_to_insert = excel_data[columns_to_insert]

    # Dynamické sestavení SQL INSERT dotazu
    placeholders = ", ".join("?" for _ in columns_to_insert)
    column_names = ", ".join(f"[{col}]" for col in columns_to_insert)
    insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    # Vložení jednotlivých řádků do databáze
    for row in data_to_insert.itertuples(index=False, name=None):
        cursor.execute(insert_query, row)

    # Uložení změn a uzavření spojení
    connection.commit()
    connection.close()
    st.success(f"Data byla úspěšně nahrána do tabulky '{table_name}'.")


# Streamlit aplikace
st.title("Nahrávání Excelu do SQLite databáze")

# Krok 1: Nahrání Excel souboru
uploaded_excel = st.file_uploader("Nahrajte Excel soubor", type=["xlsx", "xls"])
uploaded_db = st.file_uploader("Nahrajte SQLite databázi (.sldctm)", type=["sldctm", "sqlite", "db"])

if uploaded_excel and uploaded_db:
    try:
        # Načtení dat z Excel souboru
        df_turn = pd.read_excel(uploaded_excel, sheet_name="TurnOperationCost")
        df_mill = pd.read_excel(uploaded_excel, sheet_name="MillOperationCost")

        st.write("Načtená data z 'TurnOperationCost':")
        st.dataframe(df_turn)

        st.write("Načtená data z 'MillOperationCost':")
        st.dataframe(df_mill)

        # Uložení databázového souboru na disk
        sqlite_file_path = f"./{uploaded_db.name}"
        with open(sqlite_file_path, "wb") as f:
            f.write(uploaded_db.getbuffer())

        # Krok 3: Tlačítko pro nahrání dat
        if st.button("Nahrát data do databáze"):
            upload_data_to_sqlite(df_turn, sqlite_file_path, "TurnOperationCost")
            upload_data_to_sqlite(df_mill, sqlite_file_path, "MillOperationCost")

        # Krok 4: Nabídka ke stažení aktualizovaného databázového souboru
        with open(sqlite_file_path, "rb") as f:
            db_data = f.read()
        st.download_button(
            label="Stáhnout aktualizovanou databázi",
            data=db_data,
            file_name=uploaded_db.name,
            mime="application/octet-stream"
        )

        # Odstranění dočasného souboru
        os.remove(sqlite_file_path)
    except Exception as e:
        st.error(f"Chyba při zpracování: {e}")
else:
    st.info("Nahrajte oba soubory (Excel a SQLite databázi) pro pokračování.")

import streamlit as st
import pandas as pd
import sqlite3
import os


# Funkce pro nahrání dat do SQLite databáze
def upload_data_to_sqlite(excel_data, sqlite_file_path, table_name):
    # Připojení k SQLite databázi
    connection = sqlite3.connect(sqlite_file_path)
    cursor = connection.cursor()

    # Příprava dat pro vložení (bez sloupce 'id', který by měl být autoincrement)
    columns_to_insert = [col for col in excel_data.columns if col != 'id']
    data_to_insert = excel_data[columns_to_insert]

    # Dynamické sestavení SQL INSERT dotazu
    placeholders = ", ".join("?" for _ in columns_to_insert)
    column_names = ", ".join(columns_to_insert)
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
        df = pd.read_excel(uploaded_excel)
        st.write("Načtená data:")
        st.dataframe(df)

        # Uložení databázového souboru na disk
        sqlite_file_path = f"./{uploaded_db.name}"
        with open(sqlite_file_path, "wb") as f:
            f.write(uploaded_db.getbuffer())

        table_name = "TurnOperationCost"  # Pevně nastavená tabulka

        # Krok 3: Tlačítko pro nahrání dat
        if st.button("Nahrát data do databáze"):
            upload_data_to_sqlite(df, sqlite_file_path, table_name)

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

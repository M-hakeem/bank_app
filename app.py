import streamlit as st
import pandas as pd
import pdfplumber
import re


class EFTChargeAnalyzer:
    def __init__(self):
        self.raw_data = None
        self.file_type = None
        self.text_data = ""
        self.nip_data = pd.DataFrame()
        self.nip_charge_vat_data = pd.DataFrame()
        self.stamp_duty_data = pd.DataFrame()
        self.account_maintenance_fee_data = pd.DataFrame()
        self.atm_withdrawal_fee_data = pd.DataFrame()
        # New attributes for additional data
        self.otp_data = pd.DataFrame()
        self.card_maintenance_fee_data = pd.DataFrame()
        self.card_issuance_data = pd.DataFrame()
        self.forex_data = pd.DataFrame()
        self.bill_payment_data = pd.DataFrame()
        self.statement_request_data = pd.DataFrame()
        self.hardware_token_data = pd.DataFrame()
        self.loan_fees_data = pd.DataFrame()
        self.apg_charges_data = pd.DataFrame()
        self.sms_charges_data = pd.DataFrame()

    def extract_pdf_text(self, pdf_file):
        """
        Extract text from PDF pages
        """
        full_text = []
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text.append(text)
            return "\n".join(full_text) if full_text else None
        except Exception as e:
            st.error(f"Error extracting PDF: {e}")
            return None

    def extract_csv_data(self, csv_file):
        """
        Read CSV file with multiple encoding options
        """
        try:
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    self.raw_data = pd.read_csv(csv_file, encoding=encoding)
                    self.text_data = self.raw_data.to_string()
                    return self.raw_data
                except Exception:
                    continue
            st.error("Could not read CSV file with standard encodings")
            return None
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return None

    def process_document(self, uploaded_file):
        """
        Process uploaded document based on file type
        """
        if uploaded_file.name.lower().endswith('.pdf'):
            self.file_type = 'pdf'
            text_content = self.extract_pdf_text(uploaded_file)
            self.text_data = text_content
            return text_content
        elif uploaded_file.name.lower().endswith('.csv'):
            self.file_type = 'csv'
            self.raw_data = self.extract_csv_data(uploaded_file)
            return self.raw_data
        else:
            st.error("Unsupported file type. Please upload PDF or CSV.")
            return None

    def find_otp_entries(self):
        """
        Find all lines with "OTP" from the extracted text data
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        pattern = re.compile(r'.*OTP.*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        data = []
        total_otp = 0
        for match in matches:
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else 0
            total_otp += amount
            data.append({
                'Description': match,
                'Amount': amount
            })

        if not data:
            data.append({'Description': "No OTP", 'Amount': 0})

        self.otp_data = pd.DataFrame(data)
        self.otp_data.loc['Total'] = ['Total OTP Charges', total_otp]
        return self.otp_data

    # def find_card_maintenance_fee_entries(self):
    #     """
    #     Extract all 'Account Maintenance Fee' entries, ensuring comprehensive parsing and handling format inconsistencies.
    #     """
    #     if not self.text_data:
    #         print("No text data to analyze")
    #         return pd.DataFrame()
    #
    #     # Split the text data into lines
    #     lines = self.text_data.splitlines()
    #
    #     # Debug: Preview of lines
    #     print("Preview of text data:")
    #     print(lines[:20])  # Adjust as necessary for debugging
    #
    #     # Storage for results
    #     data = []
    #     total_actual = 0
    #     total_expected = 0
    #     total_overcharged = 0
    #
    #     # Helper function to extract numeric values
    #     def extract_amount(line):
    #         match = re.search(r'[\d,]+\.\d{2}', line)
    #         return float(match.group().replace(',', '')) if match else None
    #
    #     # Helper function to identify fee description lines
    #     def is_fee_line(line):
    #         return "ACCOUNT MAINTENANCE FEE" in line.upper()
    #
    #     current_date = None
    #
    #     for line in lines:
    #         # Debug: Process each line
    #         print(f"Processing line: {line}")
    #
    #         # Extract date if present
    #         date_match = re.search(r'\d{2}-[A-Z]{3}-\d{2}|\d{2}/\d{2}/\d{4}', line)
    #         if date_match:
    #             current_date = date_match.group()
    #             print(f"Found date: {current_date}")
    #
    #         # Identify maintenance fee lines
    #         if is_fee_line(line):
    #             print(f"Found fee line: {line}")
    #             amount = extract_amount(line)
    #             if amount is None:
    #                 print(f"Skipping line due to missing amount: {line}")
    #                 continue
    #
    #             # Calculate charges
    #             actual_charge = amount
    #             expected_charge = round(amount / 1000, 2)
    #             overcharged_amount = round(actual_charge - expected_charge, 2)
    #
    #             # Update totals
    #             total_actual += actual_charge
    #             total_expected += expected_charge
    #             total_overcharged += overcharged_amount
    #
    #             # Add to results
    #             data.append({
    #                 'Date of Transaction': current_date,
    #                 'Amount': actual_charge,
    #                 'Description': line.strip(),
    #                 'Actual Charge': round(actual_charge, 2),
    #                 'Expected Charge': round(expected_charge, 2),
    #                 'Overcharged Amount': round(overcharged_amount, 2),
    #             })
    #
    #     # Add summary row if data exists
    #     if data:
    #         data.append({
    #             'Date of Transaction': '---',
    #             'Amount': None,
    #             'Description': 'Total Account Maintenance Fee',
    #             'Actual Charge': round(total_actual, 2),
    #             'Expected Charge': round(total_expected, 2),
    #             'Overcharged Amount': round(total_overcharged, 2),
    #         })
    #
    #     # Convert to DataFrame
    #     result_df = pd.DataFrame(data)
    #
    #     # Debug: Print results
    #     print("Extracted DataFrame:")
    #     print(result_df)
    #
    #     return result_df

    def find_card_maintenance_fee_entries(self):
        """
        Extract all 'Account Maintenance Fee' entries, ensuring comprehensive parsing and handling format inconsistencies.
        """
        if not self.text_data:
            print("No text data to analyze")
            return pd.DataFrame()

        # Split the text data into lines
        lines = [line.strip() for line in self.text_data.splitlines() if line.strip()]

        # Debug: Preview of lines
        print("Preview of text data:")
        print(lines[:20])  # Adjust as necessary for debugging

        # Storage for results
        data = []
        total_actual = 0
        total_expected = 0
        total_overcharged = 0

        # Helper function to extract numeric values
        def extract_amount(line):
            match = re.search(r'[\d,]+\.\d{2}', line)
            return float(match.group().replace(',', '')) if match else None

        # Helper function to identify fee description lines
        def is_fee_line(line):
            return "ACCOUNT MAINTENANCE FEE" in line.upper()

        # Shared extract_date function
        def extract_date(description):
            access_bank_format = re.search(r'\d{2}-[A-Z]{3}-\s?\d{2}', description)
            zenith_bank_format = re.search(r'\d{2}/\d{2}/\d{4}', description)

            if access_bank_format:
                raw_date = access_bank_format.group().replace(" ", "")
                try:
                    return pd.to_datetime(raw_date, format='%d-%b-%y', errors='coerce').strftime('%d/%m/%Y')
                except ValueError:
                    return None
            elif zenith_bank_format:
                try:
                    return pd.to_datetime(zenith_bank_format.group(), format='%d/%m/%Y', errors='coerce').strftime(
                        '%d/%m/%Y')
                except ValueError:
                    return None

            return None

        # Extract all transactions by date
        transactions_by_date = {}
        for line in lines:
            transaction_date = extract_date(line)
            transaction_amount = extract_amount(line)

            if transaction_date and transaction_amount:
                if transaction_date not in transactions_by_date:
                    transactions_by_date[transaction_date] = 0
                transactions_by_date[transaction_date] += transaction_amount

        # Debug: Check transactions grouped by date
        print("Transactions grouped by date:")
        print(transactions_by_date)

        for line in lines:
            # Debug: Process each line
            print(f"Processing line: {line}")

            # Identify maintenance fee lines
            if is_fee_line(line):
                print(f"Found fee line: {line}")

                # Extract date from the fee description line itself
                fee_date = extract_date(line)
                print(f"Extracted fee date: {fee_date}")

                amount = extract_amount(line)
                if amount is None:
                    print(f"Skipping line due to missing amount: {line}")
                    continue

                # Calculate charges
                actual_charge = amount
                total_transactions = transactions_by_date.get(fee_date, 0)
                expected_charge = round(total_transactions / 1000, 2)
                overcharged_amount = round(actual_charge - expected_charge, 2)

                # Update totals
                total_actual += actual_charge
                total_expected += expected_charge
                total_overcharged += overcharged_amount

                # Add to results
                data.append({
                    'Date of Transaction': fee_date,
                    'Amount': actual_charge,
                    'Description': line.strip(),
                    'Actual Charge': round(actual_charge, 2),
                    'Expected Charge': round(expected_charge, 2),
                    'Overcharged Amount': round(overcharged_amount, 2),
                })

        # Add summary row if data exists
        if data:
            data.append({
                'Date of Transaction': '---',
                'Amount': None,
                'Description': 'Total Account Maintenance Fee',
                'Actual Charge': round(total_actual, 2),
                'Expected Charge': round(total_expected, 2),
                'Overcharged Amount': round(total_overcharged, 2),
            })

        # Convert to DataFrame
        result_df = pd.DataFrame(data)

        # Debug: Print results
        print("Extracted DataFrame:")
        print(result_df)

        return result_df

    def find_sms_charges(self):
        """
        Find all lines with "SMS Charges", "Notification Fee", or "Alert Fee"
        and calculate the overcharged amount.
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        pattern = re.compile(r'.*(SMS Charges|Notification Fee|Alert Fee).*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        if not matches:
            return pd.DataFrame([{
                'S/N': "No Data",
                'Date': "",
                'Description': "There was no SMS charge",
                'Transaction Amount/Actual Charge': "",
                'Expected Charge': "",
                'Overcharged Amount': ""
            }])

        data = []
        total_overcharged = 0
        serial_number = 1

        for match in matches:
            date_search = re.search(r'\d{2}/\d{2}/\d{4}', match)
            amount_search = re.search(r'[\d,]+\.\d{2}', match)

            date = date_search.group() if date_search else None
            actual_charge = float(amount_search.group().replace(',', '')) if amount_search else 0
            expected_charge = 4.00
            overcharged_amount = max(0, actual_charge - expected_charge)

            total_overcharged += overcharged_amount

            data.append({
                'S/N': serial_number,
                'Date': date,
                'Description': match,
                'Transaction Amount/Actual Charge': actual_charge,
                'Expected Charge': expected_charge,
                'Overcharged Amount': overcharged_amount
            })
            serial_number += 1

        # Add total overcharged row
        data.append({
            'S/N': "Total",
            'Date': "",
            'Description': "",
            'Transaction Amount/Actual Charge': "",
            'Expected Charge': "",
            'Overcharged Amount': total_overcharged
        })

        self.sms_charges_data = pd.DataFrame(data)
        return self.sms_charges_data

    def find_card_issuance_entries(self):
        """
        Find all lines with "Card Issuance Fee", "Card Replacement", or "Card Renewal"
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        pattern = re.compile(r'.*(Card Issuance Fee|Card Replacement|Card Renewal).*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        if not matches:
            return pd.DataFrame([{"Description": "No Card Issuance/Replacement/Renewal Fees Found", "Amount": 0}])

        data = []
        total_fee = 0
        for match in matches:
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else 0
            total_fee += amount
            data.append({
                'Description': match,
                'Amount': amount
            })

        self.card_issuance_data = pd.DataFrame(data)
        self.card_issuance_data.loc['Total'] = ['Total Card Issuance/Replacement/Renewal Fees', total_fee]
        return self.card_issuance_data

    def find_forex_entries(self):
        """
        Find all lines with "FX Charges", "Foreign Exchange Fee", or "Domiciliary Withdrawal Fee"
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        pattern = re.compile(r'.*(FX Charges|Foreign Exchange Fee|Domiciliary Withdrawal Fee).*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        if not matches:
            return pd.DataFrame([{"Description": "No Foreign Exchange Charges Found", "Amount": 0}])

        data = []
        total_fee = 0
        for match in matches:
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else 0
            total_fee += amount
            data.append({
                'Description': match,
                'Amount': amount
            })

        self.forex_data = pd.DataFrame(data)
        self.forex_data.loc['Total'] = ['Total Foreign Exchange Charges', total_fee]
        return self.forex_data

    def find_bill_payment_entries(self):
        """
        Find all lines with "Bill Payment", "Utility Charges", or "E-Channel Fee"
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        pattern = re.compile(r'.*(Bill Payment|Utility Charges|E-Channel Fee).*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        if not matches:
            return pd.DataFrame([{"Description": "No Bill Payment/Utility Charges/E-Channel Fee Found", "Amount": 0}])

        data = []
        total_fee = 0
        for match in matches:
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else 0
            total_fee += amount
            data.append({
                'Description': match,
                'Amount': amount
            })

        self.bill_payment_data = pd.DataFrame(data)
        self.bill_payment_data.loc['Total'] = ['Total Bill Payment/Utility Charges/E-Channel Fee', total_fee]
        return self.bill_payment_data

    def find_statement_request_entries(self):
        """
        Find all lines with "Statement Fee", "Account Statement Charge", or "Custom Statement"
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        pattern = re.compile(r'.*(Statement Fee|Account Statement Charge|Custom Statement).*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        if not matches:
            return pd.DataFrame(
                [{"Description": "No Statement Fee/Account Statement Charge/Custom Statement Found", "Amount": 0}])

        data = []
        total_fee = 0
        for match in matches:
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else 0
            total_fee += amount
            data.append({
                'Description': match,
                'Amount': amount
            })

        self.statement_request_data = pd.DataFrame(data)
        self.statement_request_data.loc['Total'] = ['Total Statement Fees', total_fee]
        return self.statement_request_data

    def find_hardware_token_entries(self):
        """
        Find all lines with "Token Fee", "Hardware Token Charge", "Token Replacement", "Interest Charge",
        "Loan Fee", "Restructuring Fee", or "Late Payment Fee"
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        pattern = re.compile(
            r'.*(Token Fee|Hardware Token Charge|Token Replacement|Interest Charge|Loan Fee|Restructuring Fee|Late Payment Fee).*',
            re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        if not matches:
            return pd.DataFrame([{"Description": "No Token/Loan/Interest Fees Found", "Amount": 0}])

        data = []
        total_fee = 0
        for match in matches:
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else 0
            total_fee += amount
            data.append({
                'Description': match,
                'Amount': amount
            })

        self.hardware_token_data = pd.DataFrame(data)
        self.hardware_token_data.loc['Total'] = ['Total Token/Loan/Interest Fees', total_fee]
        return self.hardware_token_data

    def find_ef_transfers(self):
        """
        Validate EFT transactions (NIP, TRF, Tra, and related charges) based on the defined charge structure.
        Calculate total amounts for key fields.
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        # Define regex patterns for each transaction type
        patterns = {
            "NIP": r'.*NIP.*',
            "NIP Charge + VAT": r'.*NIP Charge \+ VAT.*',
            "TRF": r'.*TRF.*',
            "Tra": r'.*Tra.*',
            "TRF Charge": r'.*TRF Charge.*'
        }

        def calculate_expected_charge(amount, year):
            if year >= 2020:
                if amount < 5000:
                    return 10.75
                elif 5000 <= amount <= 50000:
                    return 26.88
                else:
                    return 53.75
            else:
                if amount < 5000:
                    return 10.50
                elif 5000 <= amount <= 50000:
                    return 26.25
                else:
                    return 52.50

        def extract_date(description):
            access_bank_format = re.search(r'\d{2}-[A-Z]{3}-\s?\d{2}', description)
            zenith_bank_format = re.search(r'\d{2}/\d{2}/\d{4}', description)

            if access_bank_format:
                raw_date = access_bank_format.group().replace(" ", "")
                try:
                    return pd.to_datetime(raw_date, format='%d-%b-%y', errors='coerce').strftime('%d/%m/%Y')
                except ValueError:
                    return None
            elif zenith_bank_format:
                try:
                    return pd.to_datetime(zenith_bank_format.group(), format='%d/%m/%Y', errors='coerce').strftime(
                        '%d/%m/%Y')
                except ValueError:
                    return None

            return None

        data = []

        # Process each pattern
        for transaction_type, pattern in patterns.items():
            matches = re.findall(pattern, self.text_data, re.IGNORECASE)

            for match in matches:
                date = extract_date(match)
                amount_search = re.search(r'[\d,]+\.\d{2}', match)
                actual_charge_search = re.search(r'Charge: ([\d,]+\.\d{2})', match)

                amount = float(amount_search.group().replace(',', '')) if amount_search else None
                actual_charge = float(actual_charge_search.group(1).replace(',', '')) if actual_charge_search else None
                year = int(date.split('/')[-1]) if date else None
                expected_charge = calculate_expected_charge(amount, year) if date and amount else None

                discrepancy = (
                    actual_charge - expected_charge
                    if actual_charge is not None and expected_charge is not None
                    else None
                )

                data.append({
                    'Date': date,
                    'Transaction Type': transaction_type,
                    'Description': match,
                    'Amount': amount,
                    'Actual Charge': actual_charge,
                    'Expected Charge': expected_charge,
                    'Charge Discrepancy': discrepancy
                })

        df = pd.DataFrame(data)

        if not df.empty:
            # Calculate totals
            total_row = {
                'Date': '---',
                'Transaction Type': 'Total',
                'Description': '---',
                'Amount': df['Amount'].sum(skipna=True),
                'Actual Charge': df['Actual Charge'].sum(skipna=True),
                'Expected Charge': df['Expected Charge'].sum(skipna=True),
                'Charge Discrepancy': df['Charge Discrepancy'].sum(skipna=True)
            }
            df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

        return df

    def find_stamp_duty_entries(self):
        if not self.text_data:
            print("No text data to analyze")
            return pd.DataFrame()

        # Adjusted pattern to find relevant transactions
        pattern = re.compile(r'(STAMP DUTY CHARGE.*)', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        if not matches:
            print("No matches found for Stamp Duty Charges")  # Debugging line
            self.stamp_duty_data = pd.DataFrame(columns=[
                'Description', 'Amount', 'Actual Charge', 'Expected Charge', 'Overcharged Amount'
            ])
            return self.stamp_duty_data

        data = []

        for match in matches:
            if isinstance(match, tuple):
                match = match[0]

            print(f"Processing match: {match}")  # Debugging line

            # Extract the transaction amount
            amount_search = re.search(r'\d[\d,]*\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else None

            # Determine expected charge
            expected_charge = 50.00 if amount and amount >= 10000 else 0.00

            # Check for self-to-self transaction keyword
            is_self_to_self = bool(re.search(r'self-to-self', match, re.IGNORECASE))

            # Determine actual charge
            actual_charge = amount if not is_self_to_self else 0.00

            # Calculate overcharged amount
            overcharged_amount = max(0, actual_charge - expected_charge)

            data.append({
                'Description': match,
                'Amount': amount,
                'Actual Charge': actual_charge,
                'Expected Charge': expected_charge,
                'Overcharged Amount': overcharged_amount
            })

        self.stamp_duty_data = pd.DataFrame(data)

        # Ensure DataFrame has data before calculating total
        if not self.stamp_duty_data.empty:
            total_overcharged = self.stamp_duty_data['Overcharged Amount'].sum()

            # Add a total row
            total_row = {
                'Description': 'Total Overcharged Amount',
                'Amount': '',
                'Actual Charge': '',
                'Expected Charge': '',
                'Overcharged Amount': total_overcharged
            }
            self.stamp_duty_data = pd.concat([self.stamp_duty_data, pd.DataFrame([total_row])], ignore_index=True)

        return self.stamp_duty_data

    def find_account_maintenance_fee(self):
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        # Regex to find debit transactions
        pattern = re.compile(r'.*debit.*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        # Initialize data structure
        monthly_debit_totals = {}
        actual_charges = {}

        for match in matches:
            # Extract the transaction amount
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            amount = float(amount_search.group().replace(',', '')) if amount_search else 0

            # Extract transaction date to calculate monthly totals
            date_search = re.search(r'\d{2}/\d{2}/\d{4}', match)
            if date_search:
                transaction_date = pd.to_datetime(date_search.group(), format='%d/%m/%Y')
                month_year = transaction_date.strftime('%Y-%m')  # e.g., "2024-12"
                if month_year not in monthly_debit_totals:
                    monthly_debit_totals[month_year] = 0
                    actual_charges[month_year] = 0
                monthly_debit_totals[month_year] += amount

            # Extract actual charge for the month from the bank statement
            actual_charge_search = re.search(r'Actual Charge: ([\d,]+\.\d{2})', match)
            if actual_charge_search:
                actual_charge = float(actual_charge_search.group(1).replace(',', ''))
                actual_charges[month_year] += actual_charge

        # Prepare the output data
        data = []
        for month, total_debit in monthly_debit_totals.items():
            expected_charge = total_debit / 1000  # Divide by 1,000
            actual_charge = actual_charges.get(month, 0)
            overcharged_amount = max(0, actual_charge - expected_charge)

            data.append({
                'Month': month,
                'Total Debit': total_debit,
                'Actual Charge (₦)': round(actual_charge, 2),
                'Expected Charge (₦)': round(expected_charge, 2),
                'Overcharged Amount (₦)': round(overcharged_amount, 2),
            })

        self.account_maintenance_fee_data = pd.DataFrame(data)
        return self.account_maintenance_fee_data

    def find_atm_withdrawal_fee(self):
        """
        Calculate ATM Withdrawal Fees: Free for the first three withdrawals on other bank ATMs in a month.
        ₦35 per withdrawal after that.
        """
        if not self.text_data:
            st.error("No text data to analyze")
            return pd.DataFrame()

        # Regex to find ATM withdrawal transactions
        pattern = re.compile(r'.*ATM Withdrawal.*', re.IGNORECASE)
        matches = pattern.findall(self.text_data)

        # Initialize data structure
        withdrawals_by_month = {}
        data = []
        serial_number = 1

        for match in matches:
            # Extract transaction date
            date_search = re.search(r'\d{2}/\d{2}/\d{4}', match)
            amount_search = re.search(r'[\d,]+\.\d{2}', match)
            date = pd.to_datetime(date_search.group(), format='%d/%m/%Y') if date_search else None
            amount = float(amount_search.group().replace(',', '')) if amount_search else None

            if date:
                month_year = date.strftime('%Y-%m')  # e.g., "2024-12"
                if month_year not in withdrawals_by_month:
                    withdrawals_by_month[month_year] = 0
                withdrawals_by_month[month_year] += 1  # Increment withdrawal count for the month

                # Determine if the withdrawal incurs a fee
                withdrawal_count = withdrawals_by_month[month_year]
                fee = 35 if withdrawal_count > 3 else 0  # ₦35 after the first 3 withdrawals

                data.append({
                    'S/N': serial_number,
                    'Value Date': date.strftime('%d/%m/%Y'),
                    'Description': match,
                    'Transaction Amount': amount,
                    'Fee (₦)': fee
                })
                serial_number += 1

        # Convert the results to a DataFrame
        self.atm_withdrawal_fee_data = pd.DataFrame(data)
        return self.atm_withdrawal_fee_data


def main():
    st.title("💸 EFT Charge Analyzer")

    uploaded_file = st.sidebar.file_uploader("Upload PDF or CSV", type=['pdf', 'csv'])

    analyzer = EFTChargeAnalyzer()

    if uploaded_file is not None:
        document_data = analyzer.process_document(uploaded_file)

        if document_data is not None:
            st.write("Uploaded file processed successfully.")
            if analyzer.raw_data is not None:
                st.write(analyzer.raw_data.head())

        if analyzer.text_data:
            st.subheader("Extracted Text")
            st.text(analyzer.text_data)

        ef_transfer_entries = analyzer.find_ef_transfers()
        stamp_duty_entries = analyzer.find_stamp_duty_entries()
        account_maintenance_fee = analyzer.find_account_maintenance_fee()
        atm_withdrawal_fee = analyzer.find_atm_withdrawal_fee()

        if not ef_transfer_entries.empty:
            st.subheader("Electronic Funds Transfer (EFT) Transactions")
            st.dataframe(ef_transfer_entries)

        if not stamp_duty_entries.empty:
            st.subheader("Stamp Duty Transactions")
            st.dataframe(stamp_duty_entries)

        # New OTP Table
        otp_entries = analyzer.find_otp_entries()
        if not otp_entries.empty:
            st.subheader("OTP (One-Time Password) Charges Transactions")
            st.dataframe(otp_entries)

        # New Card Maintenance Fee Table
        card_maintenance_fee_entries = analyzer.find_card_maintenance_fee_entries()
        if not card_maintenance_fee_entries.empty:
            st.subheader("Current Account Maintenance Fee)/Account Maintenance Fee(CAM) Transactions")
            st.dataframe(card_maintenance_fee_entries)

        # New Card Issuance, Replacement, and Renewal Table
        card_issuance_entries = analyzer.find_card_issuance_entries()
        if not card_issuance_entries.empty:
            st.subheader(" Card Issuance, Replacement, and Renewal Fees Transactions")
            st.dataframe(card_issuance_entries)

        # New Forex Charges Table
        forex_entries = analyzer.find_forex_entries()
        if not forex_entries.empty:
            st.subheader("'FX Charges', 'Foreign Exchange Fee', or 'Domiciliary Withdrawal Fee'")
            st.dataframe(forex_entries)

        # New Bill Payment/Utility Charges/E-Channel Fee Table
        bill_payment_entries = analyzer.find_bill_payment_entries()
        if not bill_payment_entries.empty:
            st.subheader("'Bill Payment', 'Utility Charges', or 'E-Channel Fee'")
            st.dataframe(bill_payment_entries)

        # New Statement Fee/Account Statement Charge Table
        statement_request_entries = analyzer.find_statement_request_entries()
        if not statement_request_entries.empty:
            st.subheader("'Statement Fee', 'Account Statement Charge', or 'Custom Statement'")
            st.dataframe(statement_request_entries)

        # New Token Fee/Interest Fee Table
        hardware_token_entries = analyzer.find_hardware_token_entries()
        if not hardware_token_entries.empty:
            st.subheader(
                "'Token Fee', 'Hardware Token Charge', 'Token Replacement', 'Interest Charge', 'Loan Fee', 'Restructuring Fee', or 'Late Payment Fee'")
            st.dataframe(hardware_token_entries)

        if not account_maintenance_fee.empty:
            st.subheader("Account Maintenance Fee")
            st.dataframe(account_maintenance_fee)

        st.subheader("ATM Withdrawal Fee")
        if not atm_withdrawal_fee.empty and atm_withdrawal_fee.iloc[0]['S/N'] == "No ATM Withdrawal Fee Found":
            st.write("ATM Withdrawal Charges Transactions")
            st.dataframe(atm_withdrawal_fee)
        else:
            st.dataframe(atm_withdrawal_fee)

            # New SMS Notification Charges Table
        sms_charges = analyzer.find_sms_charges()
        if not sms_charges.empty:
            st.subheader("SMS Notification Charges")
            st.dataframe(sms_charges)


if __name__ == "__main__":
    main()

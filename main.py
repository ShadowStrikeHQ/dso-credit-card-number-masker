import argparse
import logging
import re
import os
import chardet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Masks credit card numbers within text files.")
    parser.add_argument("input_file", help="The input text file to process.")
    parser.add_argument(
        "-o", "--output_file", help="The output file to write the masked content to. If not provided, overwrites the input file."
    )
    parser.add_argument(
        "-l", "--log_file", help="The log file to write logs to. If not provided, logs to console."
    )

    return parser.parse_args()


def mask_credit_card_number(text):
    """
    Masks credit card numbers in a given string, replacing all but the last four digits with 'X'.

    Args:
        text (str): The input string to process.

    Returns:
        str: The string with credit card numbers masked.
    """
    # Credit card number regex (simplified for demonstration, adjust as needed for better accuracy)
    cc_regex = r"\b(?:\d[ -]*?){13,16}\b"
    
    def mask_match(match):
        cc_number = match.group(0)
        if len(cc_number) < 4:
          return "X" * len(cc_number)
        else:
          return "X" * (len(cc_number) - 4) + cc_number[-4:]

    return re.sub(cc_regex, mask_match, text)


def process_file(input_file, output_file=None):
    """
    Processes the input file, masks credit card numbers, and writes the output to a file.

    Args:
        input_file (str): The path to the input file.
        output_file (str, optional): The path to the output file. If None, overwrites the input file.
    """

    try:
        # Detect the encoding of the file
        with open(input_file, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        
        # Handle NoneType or unsupported encodings:
        if not encoding:
            logging.error(f"Failed to detect encoding for {input_file}. Using UTF-8 as fallback.")
            encoding = 'utf-8'

        if encoding.lower() == 'ascii': #ascii is very limited; may be better to upgrade it to utf-8
            encoding = 'utf-8'

        if encoding.lower() == 'windows-1252': #upgrade
            encoding = 'utf-8'


        logging.info(f"Detected encoding: {encoding} for file {input_file}")
      
        with open(input_file, 'r', encoding=encoding) as infile:
            content = infile.read()
        
        masked_content = mask_credit_card_number(content)
        
        if output_file:
            with open(output_file, 'w', encoding=encoding) as outfile:
                outfile.write(masked_content)
            logging.info(f"Successfully masked credit card numbers in {input_file} and wrote to {output_file}")
        else:
            with open(input_file, 'w', encoding=encoding) as outfile:
                outfile.write(masked_content)
            logging.info(f"Successfully masked credit card numbers in {input_file} (overwritten)")

    except FileNotFoundError:
        logging.error(f"File not found: {input_file}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def main():
    """
    Main function to execute the credit card number masking tool.
    """
    args = setup_argparse()

    if args.log_file:
        # Create a file handler and set the formatter
        file_handler = logging.FileHandler(args.log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the root logger
        logging.getLogger().addHandler(file_handler)
    

    # Validate input file
    if not os.path.isfile(args.input_file):
        logging.error(f"Invalid input file: {args.input_file}")
        return
      
    #Validate input file
    if args.output_file:
        if os.path.exists(args.output_file):
            logging.warning(f"Output file {args.output_file} already exists.  Will overwrite")
    

    process_file(args.input_file, args.output_file)


if __name__ == "__main__":
    """
    Entry point of the script.
    """
    main()

# Usage Examples:
# 1. Mask credit card numbers in input.txt and overwrite the input file:
#    python main.py input.txt

# 2. Mask credit card numbers in input.txt and save the output to output.txt:
#    python main.py input.txt -o output.txt

# 3. Mask credit card numbers in input.txt, save the output to output.txt, and log to a file:
#    python main.py input.txt -o output.txt -l app.log
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import os

from bs4 import BeautifulSoup
import configparser
import csv


def run() -> None:
    # Setup logging
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logging.basicConfig()
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.DEBUG)
    
    # Parse command line options
    parser = argparse.ArgumentParser(
        description='Converts KeePass XML file to 1Password CSV')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    args = parser.parse_args()
    
    # Read config file
    config = configparser.SafeConfigParser()
    config.read(os.path.join('etc', script_name + '.conf'))
    
    passwords_xml = BeautifulSoup(open(config.get('General', 'input'), encoding='utf-8'))
    logger.info('KeePass XML file is opened')
    
    fields = set()
    entries = []
    delimeter = ';'
    
    for group_xml in passwords_xml.find_all('group'):
        for entry_xml in group_xml.children:
            if entry_xml.name != 'entry':
                continue
                
            entry = {}
            
            for string_xml in entry_xml.children:
                if string_xml.name != 'string':
                    continue
                    
                key = string_xml.key.string
                value = string_xml.value.string
                
                if key and value:
                    key = key.replace(delimeter, '<delimeter>')
                    fields.add(key)
                    
                    value = value.replace(delimeter, '<delimeter>')
                    entry[key] = value
                    
            # entry['title'] = normalize(entry_xml.title.string)
            # if entry_xml.username.string:
            #     entry['username'] = normalize(entry_xml.username.string)
            # if entry_xml.password.string:
            #     entry['password'] = normalize(entry_xml.password.string)
            # if entry_xml.url.string:
            #     entry['url'] = normalize(entry_xml.url.string.replace('http://', ''))
            # if entry_xml.comment.contents:
            #     # Convert <br> to line breaks:
            #     notes = '\n'.join(element for element in entry_xml.comment.contents if element.name != 'br')
            #     entry['notes'] = normalize(notes)
                
            entries.append(entry)
            
    # Prepare output file
    with open(config.get('General', 'output'), 'w', encoding='utf-8', newline='') as output:
        dialect = csv.excel
        dialect.delimiter = delimeter
        
        writer = csv.DictWriter(output, fieldnames=fields, dialect=dialect)
        writer.writeheader()
        writer.writerows(entries)
        
        logger.info('1Password CSV file is written')
        
        
if __name__ == '__main__':
    run()
    
"""
Data Validation Tool
Validate email, phone, URLs, credit cards, dates, and custom patterns
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class DataValidator:
    """Validate various data types and formats"""
    
    @staticmethod
    def email(value: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def phone(value: str, country_code: str = 'US') -> bool:
        """Validate phone number format"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', value)
        
        patterns = {
            'US': r'^\+?1?[0-9]{10}$',
            'UK': r'^\+?44[0-9]{10}$',
            'CA': r'^\+?1[0-9]{10}$',
            'INTL': r'^\+?[0-9]{10,15}$'
        }
        
        pattern = patterns.get(country_code, patterns['INTL'])
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def url(value: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def ipv4(value: str) -> bool:
        """Validate IPv4 address"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def credit_card(value: str) -> bool:
        """Validate credit card using Luhn algorithm"""
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-]', '', value)
        
        if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
            return False
        
        # Luhn algorithm
        total = 0
        for i, digit in enumerate(reversed(cleaned)):
            d = int(digit)
            if i % 2 == 1:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        
        return total % 10 == 0
    
    @staticmethod
    def date(value: str, format_str: str = '%Y-%m-%d') -> bool:
        """Validate date format"""
        try:
            datetime.strptime(value, format_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def username(value: str, min_length: int = 3, max_length: int = 20) -> bool:
        """Validate username (alphanumeric and underscore only)"""
        if not (min_length <= len(value) <= max_length):
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def password_strength(value: str) -> Tuple[bool, str]:
        """Validate and score password strength"""
        if len(value) < 8:
            return False, "Too short (min 8 chars)"
        
        score = 0
        feedback = []
        
        if len(value) >= 12:
            score += 1
        if re.search(r'[a-z]', value):
            score += 1
        else:
            feedback.append("Add lowercase letters")
        if re.search(r'[A-Z]', value):
            score += 1
        else:
            feedback.append("Add uppercase letters")
        if re.search(r'[0-9]', value):
            score += 1
        else:
            feedback.append("Add numbers")
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', value):
            score += 1
        else:
            feedback.append("Add special characters")
        
        strength_levels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong", 5: "Very Strong"}
        strength = strength_levels.get(score, "Unknown")
        suggestions = " | ".join(feedback) if feedback else "Excellent password"
        
        return score >= 3, f"{strength} ({score}/5) - {suggestions}"
    
    @staticmethod
    def zip_code(value: str, country_code: str = 'US') -> bool:
        """Validate zip/postal codes"""
        patterns = {
            'US': r'^\d{5}(-\d{4})?$',  # 12345 or 12345-6789
            'CA': r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$',  # A1A 1A1
            'UK': r'^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$',
            'DE': r'^\d{5}$',
        }
        
        pattern = patterns.get(country_code)
        if not pattern:
            return False
        return bool(re.match(pattern, value))
    
    @staticmethod
    def custom_pattern(value: str, pattern: str) -> bool:
        """Validate against custom regex pattern"""
        try:
            return bool(re.match(pattern, value))
        except re.error:
            return False


class DataValidationReport:
    """Generate validation reports"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, field: str, value: str, validator_name: str, is_valid: bool):
        """Add validation result"""
        self.results.append({
            'field': field,
            'value': value,
            'validator': validator_name,
            'valid': is_valid
        })
    
    def print_report(self):
        """Print validation report"""
        if not self.results:
            print("No results to report")
            return
        
        print("\n" + "="*60)
        print("✓ VALIDATION REPORT")
        print("="*60)
        
        valid_count = sum(1 for r in self.results if r['valid'])
        total_count = len(self.results)
        
        for result in self.results:
            status = "✅ VALID" if result['valid'] else "❌ INVALID"
            print(f"{status} | {result['field']}: {result['value']}")
            print(f"         ({result['validator']})")
        
        print("="*60)
        print(f"Summary: {valid_count}/{total_count} fields valid ({valid_count*100//total_count}%)")
        print("="*60 + "\n")


def main():
    print("🔍 Data Validation Tool\n")
    
    validator = DataValidator()
    report = DataValidationReport()
    
    print("Validation options:")
    print("1. Email")
    print("2. Phone")
    print("3. URL")
    print("4. IPv4")
    print("5. Credit Card")
    print("6. Date")
    print("7. Username")
    print("8. Password Strength")
    print("9. Zip Code")
    print("10. Validate multiple fields (batch)")
    print("11. Exit")
    
    while True:
        choice = input("\nSelect validation (1-11): ").strip()
        
        if choice == '1':
            email = input("Enter email: ").strip()
            is_valid = validator.email(email)
            print(f"{'✅' if is_valid else '❌'} Email is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '2':
            phone = input("Enter phone: ").strip()
            country = input("Country code (US/UK/CA, default: US): ").strip() or 'US'
            is_valid = validator.phone(phone, country)
            print(f"{'✅' if is_valid else '❌'} Phone is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '3':
            url = input("Enter URL: ").strip()
            is_valid = validator.url(url)
            print(f"{'✅' if is_valid else '❌'} URL is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '4':
            ip = input("Enter IPv4: ").strip()
            is_valid = validator.ipv4(ip)
            print(f"{'✅' if is_valid else '❌'} IPv4 is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '5':
            cc = input("Enter credit card: ").strip()
            is_valid = validator.credit_card(cc)
            print(f"{'✅' if is_valid else '❌'} Credit card is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '6':
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            is_valid = validator.date(date_str)
            print(f"{'✅' if is_valid else '❌'} Date is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '7':
            username = input("Enter username: ").strip()
            is_valid = validator.username(username)
            print(f"{'✅' if is_valid else '❌'} Username is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '8':
            password = input("Enter password: ").strip()
            is_strong, feedback = validator.password_strength(password)
            print(f"{'✅' if is_strong else '⚠️'} {feedback}")
        
        elif choice == '9':
            zip_code = input("Enter zip code: ").strip()
            country = input("Country code (US/CA/UK/DE, default: US): ").strip() or 'US'
            is_valid = validator.zip_code(zip_code, country)
            print(f"{'✅' if is_valid else '❌'} Zip code is {'valid' if is_valid else 'invalid'}")
        
        elif choice == '10':
            print("\nBatch validation - enter field:value pairs")
            print("Example: email:test@example.com, phone:1234567890, url:https://example.com")
            batch_str = input("Enter pairs: ").strip()
            
            for pair in batch_str.split(','):
                try:
                    field, value = pair.strip().split(':', 1)
                    field = field.strip()
                    value = value.strip()
                    
                    if field == 'email':
                        is_valid = validator.email(value)
                    elif field == 'phone':
                        is_valid = validator.phone(value)
                    elif field == 'url':
                        is_valid = validator.url(value)
                    else:
                        is_valid = False
                    
                    report.add_result(field, value, field.upper(), is_valid)
                except ValueError:
                    print(f"❌ Invalid format: {pair}")
            
            report.print_report()
        
        elif choice == '11':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()

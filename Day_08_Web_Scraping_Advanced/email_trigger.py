"""
Email-Based Trigger System
Monitor conditions and send alerts via email
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Callable, Optional
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Send emails via SMTP"""

    def __init__(self, sender_email: str, password: str, smtp_server: str = "smtp.gmail.com", port: int = 587):
        """Initialize email service"""
        self.sender_email = sender_email
        self.password = password
        self.smtp_server = smtp_server
        self.port = port

    def send_email(self, recipient: str, subject: str, body: str, html: bool = False) -> bool:
        """Send email"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient

            if html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, recipient, message.as_string())

            logger.info(f"✅ Email sent to {recipient}: {subject}")
            return True

        except Exception as e:
            logger.error(f"❌ Email failed: {e}")
            return False


class TriggerManager:
    """Manage conditions and triggers"""

    def __init__(self, email_service: EmailService):
        """Initialize trigger manager"""
        self.email_service = email_service
        self.triggers: Dict[str, Dict] = {}
        self.triggered_count = 0

    def add_trigger(self, trigger_id: str, condition: Callable[[], bool], 
                   action: Callable[[str, str], None], description: str = "") -> None:
        """Add a trigger (condition + action)"""
        self.triggers[trigger_id] = {
            'condition': condition,
            'action': action,
            'description': description,
            'created': datetime.now().isoformat(),
            'triggered_count': 0
        }
        logger.info(f"✅ Trigger added: {trigger_id}")

    def check_triggers(self) -> None:
        """Check all triggers"""
        for trigger_id, trigger in self.triggers.items():
            try:
                if trigger['condition']():
                    logger.warning(f"🚨 Trigger fired: {trigger_id}")
                    trigger['triggered_count'] += 1
                    trigger['action'](trigger_id, trigger['description'])
                    self.triggered_count += 1
            except Exception as e:
                logger.error(f"❌ Error checking {trigger_id}: {e}")

    def monitor(self, check_interval: int = 60) -> None:
        """Continuously monitor triggers"""
        logger.info(f"🔔 Monitoring {len(self.triggers)} triggers every {check_interval}s")
        
        try:
            while True:
                self.check_triggers()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("⏹️  Monitoring stopped")

    def get_stats(self) -> Dict:
        """Get trigger statistics"""
        return {
            'total_triggers': len(self.triggers),
            'total_triggered': self.triggered_count,
            'triggers': {
                tid: {
                    'description': t['description'],
                    'triggered_count': t['triggered_count'],
                    'created': t['created']
                }
                for tid, t in self.triggers.items()
            }
        }


class StockAlertTrigger:
    """Example: Stock price alert trigger"""

    def __init__(self, stock_symbol: str, target_price: float, comparison: str = "below"):
        """Initialize stock alert"""
        self.symbol = stock_symbol
        self.target_price = target_price
        self.comparison = comparison  # "above" or "below"
        self.current_price = None

    def check(self) -> bool:
        """Check if alert condition is met"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period='1d')
            
            if not data.empty:
                self.current_price = data.iloc[-1]['Close']
                
                if self.comparison == "below" and self.current_price < self.target_price:
                    return True
                elif self.comparison == "above" and self.current_price > self.target_price:
                    return True
        except Exception as e:
            logger.error(f"❌ Error checking stock: {e}")
        
        return False

    def format_alert(self) -> str:
        """Format alert message"""
        return f"""
🚨 Stock Alert: {self.symbol}

Current Price: ${self.current_price:.2f}
Target Price: ${self.target_price:.2f}
Condition: Price is {self.comparison} target

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


class WeatherAlertTrigger:
    """Example: Weather alert trigger"""

    def __init__(self, city: str, condition: str, alert_api_key: str = None):
        """Initialize weather alert"""
        self.city = city
        self.condition = condition  # "rain", "snow", "extreme_temp", etc.
        self.api_key = alert_api_key

    def check(self) -> bool:
        """Check weather condition"""
        try:
            import requests
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": self.city,
                "appid": self.api_key
            }
            
            response = requests.get(base_url, params=params, timeout=5)
            data = response.json()
            
            weather = data.get('weather', [{}])[0].get('main', '').lower()
            temp = data.get('main', {}).get('temp', 0)
            
            if self.condition == "rain" and "rain" in weather:
                return True
            elif self.condition == "snow" and "snow" in weather:
                return True
            elif self.condition == "extreme_temp" and (temp > 40 or temp < -20):
                return True
        
        except Exception as e:
            logger.error(f"❌ Error checking weather: {e}")
        
        return False


def demo_trigger_system():
    """Demo trigger system"""
    print("📧 Email-Based Trigger System Demo\n")
    
    print("Setup:")
    print("1. Enable 2FA on your email account")
    print("2. Generate app-specific password")
    print("3. Configure sender_email and app_password")
    print("\nFeatures:")
    print("✓ Customizable triggers")
    print("✓ Email notifications")
    print("✓ Stock price alerts")
    print("✓ Weather alerts")
    print("✓ Continuous monitoring")
    
    # Example (would need real credentials to run)
    # email_service = EmailService("your_email@gmail.com", "your_app_password")
    # manager = TriggerManager(email_service)


if __name__ == "__main__":
    demo_trigger_system()

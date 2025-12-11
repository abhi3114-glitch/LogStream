import asyncio
from collections import deque
from typing import List, Dict, Optional, Callable
import datetime
import re

class LogStorage:
    def __init__(self, max_size: int = 10000):
        self.logs: deque = deque(maxlen=max_size)
        self.listeners: List[Callable] = []
        
    async def add_log(self, raw_message: str, protocol: str, host: str):
        """Parse and store a new log entry."""
        log_entry = self._parse(raw_message, protocol, host)
        self.logs.append(log_entry)
        # Notify listeners (WebSockets)
        for listener in self.listeners:
            try:
                await listener(log_entry)
            except Exception:
                pass # remove dead listener logic handled elsewhere

    def subscribe(self, listener: Callable):
        self.listeners.append(listener)
    
    def unsubscribe(self, listener: Callable):
        if listener in self.listeners:
            self.listeners.remove(listener)

    def search(self, query: str = None, level: str = None, service: str = None, limit: int = 100) -> List[Dict]:
        results = []
        # Reverse iteration for most recent logs first
        for log in reversed(self.logs):
            if len(results) >= limit:
                break
            
            if level and log.get("level") != level:
                continue
            
            if service and log.get("service") != service:
                continue
            
            if query and query.lower() not in log.get("raw", "").lower():
                continue
                
            results.append(log)
        
        return results

    def _parse(self, raw: str, protocol: str, host: str) -> Dict:
        """Basic parsing logic. Can be promoted to a separate parser class."""
        timestamp = datetime.datetime.now().isoformat()
        level = "INFO"
        service = "unknown"
        
        # Simple heuristic parsing (can be improved)
        # Example: "ERROR [auth-service] User login failed"
        
        lower_raw = raw.lower()
        if "error" in lower_raw:
            level = "ERROR"
        elif "warn" in lower_raw or "warning" in lower_raw:
            level = "WARN"
        elif "debug" in lower_raw:
            level = "DEBUG"
            
        # Try to extract service name in brackets [service-name]
        service_match = re.search(r"\[([a-zA-Z0-9_-]+)\]", raw)
        if service_match:
            service = service_match.group(1)
            
        return {
            "timestamp": timestamp,
            "level": level,
            "service": service,
            "protocol": protocol,
            "host": host,
            "raw": raw.strip()
        }

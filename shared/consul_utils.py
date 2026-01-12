"""
Consul Service Discovery Utilities
Đăng ký và khám phá services qua Consul
"""
import os
import socket
import atexit
import logging
from typing import Optional, Dict, List
import requests

logger = logging.getLogger(__name__)


class ConsulClient:
    """Client để tương tác với Consul"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.environ.get('CONSUL_HOST', 'localhost')
        self.port = port or int(os.environ.get('CONSUL_PORT', 8500))
        self.base_url = f'http://{self.host}:{self.port}'
        self._registered_services = []
        self._available_cache = None
        self._cache_time = 0
        self._cache_ttl = 30
    
    def is_available(self) -> bool:
        """Kiểm tra Consul có đang chạy không (với caching)"""
        import time
        current_time = time.time()
        
        # Return cached result if still valid
        if self._available_cache is not None and (current_time - self._cache_time) < self._cache_ttl:
            return self._available_cache
        
        try:
            response = requests.get(f'{self.base_url}/v1/status/leader', timeout=1)
            self._available_cache = response.status_code == 200
        except:
            self._available_cache = False
        
        self._cache_time = current_time
        return self._available_cache
    
    def register_service(
        self,
        name: str,
        service_id: str,
        port: int,
        host: str = None,
        tags: List[str] = None,
        health_check_url: str = None,
        health_check_interval: str = '10s'
    ) -> bool:
        """
        Đăng ký service với Consul
        
        Args:
            name: Tên service (vd: product_service)
            service_id: ID unique của service instance
            port: Port service đang chạy
            host: Host của service (default: localhost)
            tags: Tags để phân loại service
            health_check_url: URL để Consul kiểm tra health
            health_check_interval: Khoảng thời gian check (default: 10s)
        
        Returns:
            True nếu đăng ký thành công
        """
        if not self.is_available():
            logger.warning("Consul không khả dụng, bỏ qua đăng ký service")
            return False
        
        host = host or self._get_local_ip()
        
        service_data = {
            'ID': service_id,
            'Name': name,
            'Address': host,
            'Port': port,
            'Tags': tags or ['flask', 'soa', 'minimarket'],
        }
        
        # Thêm health check nếu có
        if health_check_url:
            service_data['Check'] = {
                'HTTP': health_check_url,
                'Interval': health_check_interval,
                'Timeout': '5s',
                'DeregisterCriticalServiceAfter': '30s'
            }
        
        try:
            response = requests.put(
                f'{self.base_url}/v1/agent/service/register',
                json=service_data,
                timeout=5
            )
            
            if response.status_code == 200:
                self._registered_services.append(service_id)
                logger.info(f"✓ Đã đăng ký service '{name}' (ID: {service_id}) với Consul")
                return True
            else:
                logger.error(f"Lỗi đăng ký service: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Không thể đăng ký service với Consul: {e}")
            return False
    
    def deregister_service(self, service_id: str) -> bool:
        """Hủy đăng ký service khỏi Consul"""
        if not self.is_available():
            return False
        
        try:
            response = requests.put(
                f'{self.base_url}/v1/agent/service/deregister/{service_id}',
                timeout=5
            )
            
            if response.status_code == 200:
                if service_id in self._registered_services:
                    self._registered_services.remove(service_id)
                logger.info(f"✓ Đã hủy đăng ký service ID: {service_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Không thể hủy đăng ký service: {e}")
            return False
    
    def deregister_all(self):
        """Hủy đăng ký tất cả services đã đăng ký"""
        for service_id in list(self._registered_services):
            self.deregister_service(service_id)
    
    def discover_service(self, name: str, healthy_only: bool = True) -> List[Dict]:
        """
        Tìm các instances của một service
        
        Args:
            name: Tên service cần tìm
            healthy_only: Chỉ trả về services healthy
        
        Returns:
            Danh sách các service instances
        """
        if not self.is_available():
            return []
        
        try:
            if healthy_only:
                url = f'{self.base_url}/v1/health/service/{name}?passing=true'
            else:
                url = f'{self.base_url}/v1/catalog/service/{name}'
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if healthy_only:
                    # Format từ health endpoint
                    services = []
                    for item in data:
                        service = item.get('Service', {})
                        services.append({
                            'id': service.get('ID'),
                            'name': service.get('Service'),
                            'address': service.get('Address'),
                            'port': service.get('Port'),
                            'tags': service.get('Tags', [])
                        })
                    return services
                else:
                    # Format từ catalog endpoint
                    return [{
                        'id': s.get('ServiceID'),
                        'name': s.get('ServiceName'),
                        'address': s.get('ServiceAddress') or s.get('Address'),
                        'port': s.get('ServicePort'),
                        'tags': s.get('ServiceTags', [])
                    } for s in data]
            
            return []
        except Exception as e:
            logger.error(f"Lỗi tìm service: {e}")
            return []
    
    def get_service_url(self, name: str) -> Optional[str]:
        """
        Lấy URL của một service (load balance round-robin đơn giản)
        
        Args:
            name: Tên service
        
        Returns:
            URL của service hoặc None
        """
        services = self.discover_service(name)
        
        if services:
            # Lấy service đầu tiên (có thể implement round-robin sau)
            service = services[0]
            return f"http://{service['address']}:{service['port']}"
        
        return None
    
    def get_all_services(self) -> Dict[str, List[str]]:
        """Lấy danh sách tất cả services đã đăng ký"""
        if not self.is_available():
            return {}
        
        try:
            response = requests.get(f'{self.base_url}/v1/catalog/services', timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except:
            return {}
    
    def get_service_health(self, name: str) -> List[Dict]:
        """Lấy thông tin health của các instances của service"""
        if not self.is_available():
            return []
        
        try:
            response = requests.get(
                f'{self.base_url}/v1/health/service/{name}',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data:
                    service = item.get('Service', {})
                    checks = item.get('Checks', [])
                    
                    # Xác định status tổng thể
                    status = 'passing'
                    for check in checks:
                        if check.get('Status') == 'critical':
                            status = 'critical'
                            break
                        elif check.get('Status') == 'warning':
                            status = 'warning'
                    
                    results.append({
                        'id': service.get('ID'),
                        'name': service.get('Service'),
                        'address': service.get('Address'),
                        'port': service.get('Port'),
                        'status': status,
                        'checks': checks
                    })
                
                return results
            return []
        except Exception as e:
            logger.error(f"Lỗi lấy health: {e}")
            return []
    
    def _get_local_ip(self) -> str:
        """Lấy IP local của machine"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return 'localhost'


# Global instance
consul_client = ConsulClient()


def register_flask_service(app, name: str, port: int, tags: List[str] = None):
    """
    Helper function để đăng ký Flask app với Consul
    
    Usage:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'product_service', 5001)
    """
    import uuid
    
    service_id = f"{name}-{uuid.uuid4().hex[:8]}"
    host = os.environ.get('SERVICE_HOST', 'localhost')
    health_url = f"http://{host}:{port}/health"
    
    # Đăng ký service
    success = consul_client.register_service(
        name=name,
        service_id=service_id,
        port=port,
        host=host,
        tags=tags or ['flask', 'soa'],
        health_check_url=health_url
    )
    
    if success:
        # Đăng ký callback để hủy đăng ký khi app shutdown
        atexit.register(lambda: consul_client.deregister_service(service_id))
    
    return service_id

"""
Security Manager Module

This module handles secure data operations, encryption, and privacy compliance.
"""

import logging
import hashlib
import secrets
import json
import random
import math
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256 = "aes-256"
    RSA = "rsa"
    CHACHA20 = "chacha20"


class DataClassification(Enum):
    """Data sensitivity classification"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PrivacyRegulation(Enum):
    """Privacy regulations"""
    GDPR = "gdpr"  # EU General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOC2 = "soc2"  # Service Organization Control 2


@dataclass
class DataAsset:
    """Represents a data asset with security metadata"""
    asset_id: str
    classification: DataClassification
    encrypted: bool
    created_at: datetime
    last_accessed: datetime
    owner: Optional[str]
    retention_days: int
    metadata: Dict[str, Any]


@dataclass
class AuditLogEntry:
    """Security audit log entry"""
    timestamp: datetime
    action: str
    user_id: Optional[str]
    asset_id: Optional[str]
    success: bool
    details: Dict[str, Any]


class SecurityManager:
    """
    Security and data privacy management system.
    
    Features:
    - Data encryption/decryption
    - Access control
    - Privacy compliance (GDPR, CCPA, etc.)
    - Audit logging
    - Secure data handling
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SecurityManager")
        self.logger.setLevel(logging.INFO)
        
        # Data assets registry
        self.data_assets: Dict[str, DataAsset] = {}
        
        # Audit log
        self.audit_log: List[AuditLogEntry] = []
        
        # Encryption keys (in production, use proper key management)
        self._encryption_keys: Dict[str, bytes] = {}
        
        # Privacy compliance settings
        self.compliance_regulations = [PrivacyRegulation.GDPR]
        
        self.logger.info("SecurityManager initialized")
    
    def encrypt_data(
        self,
        data: str,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    ) -> Dict[str, Any]:
        """
        Encrypt data using specified algorithm.
        
        Note: This is a simplified implementation for demonstration.
        Production systems should use proper cryptography libraries
        like `cryptography` or `PyCryptodome`.
        
        Args:
            data: Data to encrypt
            algorithm: Encryption algorithm to use
            
        Returns:
            Dictionary with encrypted data and metadata
        """
        import base64
        
        # Generate a random key for this encryption
        key = secrets.token_bytes(32)
        key_id = hashlib.sha256(key).hexdigest()[:16]
        self._encryption_keys[key_id] = key
        
        # Simple XOR encryption for demonstration
        # In production, use proper AES-256-GCM or similar
        encrypted_bytes = bytes([
            b ^ key[i % len(key)]
            for i, b in enumerate(data.encode('utf-8'))
        ])
        
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        self._log_audit(
            action="encrypt_data",
            success=True,
            details={"algorithm": algorithm.value, "key_id": key_id}
        )
        
        self.logger.debug(f"Encrypted data using {algorithm.value}")
        
        return {
            "encrypted_data": encrypted_b64,
            "algorithm": algorithm.value,
            "key_id": key_id,
            "checksum": hashlib.sha256(data.encode()).hexdigest()
        }
    
    def decrypt_data(
        self,
        encrypted_data: str,
        key_id: str,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256
    ) -> Optional[str]:
        """
        Decrypt data using specified key.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            key_id: Key identifier
            algorithm: Encryption algorithm used
            
        Returns:
            Decrypted data or None if decryption fails
        """
        import base64
        
        if key_id not in self._encryption_keys:
            self.logger.error(f"Encryption key not found: {key_id}")
            self._log_audit(
                action="decrypt_data",
                success=False,
                details={"error": "key_not_found"}
            )
            return None
        
        key = self._encryption_keys[key_id]
        
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # XOR decryption (matching encryption)
            decrypted_bytes = bytes([
                b ^ key[i % len(key)]
                for i, b in enumerate(encrypted_bytes)
            ])
            
            decrypted = decrypted_bytes.decode('utf-8')
            
            self._log_audit(
                action="decrypt_data",
                success=True,
                details={"algorithm": algorithm.value, "key_id": key_id}
            )
            
            return decrypted
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            self._log_audit(
                action="decrypt_data",
                success=False,
                details={"error": str(e)}
            )
            return None
    
    def hash_data(self, data: str, algorithm: str = "sha256") -> str:
        """
        Create a cryptographic hash of data.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512)
        """
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def register_data_asset(
        self,
        asset_id: str,
        classification: DataClassification,
        encrypted: bool = False,
        owner: Optional[str] = None,
        retention_days: int = 365
    ) -> DataAsset:
        """Register a data asset for tracking"""
        asset = DataAsset(
            asset_id=asset_id,
            classification=classification,
            encrypted=encrypted,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            owner=owner,
            retention_days=retention_days,
            metadata={}
        )
        
        self.data_assets[asset_id] = asset
        
        self._log_audit(
            action="register_asset",
            asset_id=asset_id,
            success=True,
            details={"classification": classification.value}
        )
        
        self.logger.info(f"Registered data asset: {asset_id}")
        return asset
    
    def check_gdpr_compliance(self, asset_id: str) -> Dict[str, Any]:
        """
        Check GDPR compliance for a data asset.
        
        GDPR requires:
        - Right to access
        - Right to rectification
        - Right to erasure (right to be forgotten)
        - Right to data portability
        - Data minimization
        - Storage limitation
        """
        if asset_id not in self.data_assets:
            return {
                "compliant": False,
                "issues": ["Asset not registered"]
            }
        
        asset = self.data_assets[asset_id]
        issues = []
        
        # Check if sensitive data is encrypted
        if asset.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            if not asset.encrypted:
                issues.append("Sensitive data should be encrypted")
        
        # Check retention period (GDPR requires reasonable retention)
        # Default max is 7 years, but this should be configured based on data type
        max_retention_days = 2555  # ~7 years - configurable threshold
        if asset.retention_days > max_retention_days:
            issues.append(f"Retention period exceeds recommended maximum ({max_retention_days} days)")
        
        # Check if data has an owner (accountability)
        if not asset.owner:
            issues.append("Data should have an assigned owner")
        
        compliant = len(issues) == 0
        
        return {
            "regulation": "GDPR",
            "asset_id": asset_id,
            "compliant": compliant,
            "issues": issues,
            "classification": asset.classification.value,
            "encrypted": asset.encrypted
        }
    
    def anonymize_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize personally identifiable information (PII).
        
        This is a simplified implementation. Production systems
        should use proper anonymization techniques.
        """
        pii_fields = ["name", "email", "phone", "ssn", "address", "ip_address"]
        
        anonymized = data.copy()
        
        for field in pii_fields:
            if field in anonymized:
                # Replace with hashed value
                original_value = str(anonymized[field])
                anonymized[field] = hashlib.sha256(original_value.encode()).hexdigest()[:16]
        
        self._log_audit(
            action="anonymize_pii",
            success=True,
            details={"fields_anonymized": len([f for f in pii_fields if f in data])}
        )
        
        return anonymized
    
    def apply_differential_privacy(
        self,
        data: List[float],
        epsilon: float = 1.0,
        sensitivity: float = 1.0
    ) -> List[float]:
        """
        Apply differential privacy using Laplace mechanism.
        
        Differential privacy protects individual data points by adding
        calibrated noise to query results or aggregated data.
        
        Args:
            data: Original data values
            epsilon: Privacy budget (lower = more privacy, more noise)
            sensitivity: Query sensitivity (max change from one record)
            
        Returns:
            Data with added noise for privacy protection
        """
        # Calculate Laplace noise scale
        scale = sensitivity / epsilon
        
        # Add Laplace noise to each data point
        noisy_data = []
        for value in data:
            # Laplace noise: sample from Laplace distribution using inverse transform
            # U ~ Uniform(0, 1), then noise = -scale * sign(U - 0.5) * log(1 - 2|U - 0.5|)
            uniform = random.random()
            
            # Determine sign
            if uniform < 0.5:
                sign = 1
                uniform_shifted = 0.5 - uniform
            else:
                sign = -1
                uniform_shifted = uniform - 0.5
            
            # Generate Laplace noise using inverse CDF
            laplace_noise = -scale * sign * math.log(1 - 2 * uniform_shifted)
            
            noisy_value = value + laplace_noise
            noisy_data.append(noisy_value)
        
        self._log_audit(
            action="apply_differential_privacy",
            success=True,
            details={
                "epsilon": epsilon,
                "sensitivity": sensitivity,
                "data_points": len(data)
            }
        )
        
        self.logger.info(f"Applied differential privacy (ε={epsilon}) to {len(data)} data points")
        
        return noisy_data
    
    def aggregate_with_privacy(
        self,
        data: List[float],
        aggregation_type: str = "mean",
        epsilon: float = 1.0
    ) -> float:
        """
        Perform aggregation with differential privacy.
        
        Args:
            data: Data to aggregate
            aggregation_type: Type of aggregation (mean, sum, count)
            epsilon: Privacy budget
            
        Returns:
            Aggregated value with privacy protection
        """
        if not data:
            return 0.0
        
        if aggregation_type == "mean":
            true_value = sum(data) / len(data)
            sensitivity = (max(data) - min(data)) / len(data) if len(data) > 1 else 1.0
        elif aggregation_type == "sum":
            true_value = sum(data)
            sensitivity = max(abs(min(data)), abs(max(data)))
        elif aggregation_type == "count":
            true_value = len(data)
            sensitivity = 1.0
        else:
            raise ValueError(f"Unsupported aggregation type: {aggregation_type}")
        
        # Apply differential privacy
        noisy_result = self.apply_differential_privacy([true_value], epsilon, sensitivity)[0]
        
        self.logger.debug(f"Aggregated {len(data)} values with privacy: {aggregation_type}")
        
        return noisy_result
    
    def check_ccpa_compliance(self, asset_id: str) -> Dict[str, Any]:
        """
        Check CCPA (California Consumer Privacy Act) compliance.
        
        CCPA requires:
        - Right to know what data is collected
        - Right to delete personal information
        - Right to opt-out of data sale
        - Data security requirements
        """
        if asset_id not in self.data_assets:
            return {
                "compliant": False,
                "issues": ["Asset not registered"]
            }
        
        asset = self.data_assets[asset_id]
        issues = []
        
        # Check if personal information is protected
        if asset.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            if not asset.encrypted:
                issues.append("Personal information should be encrypted")
        
        # Check data retention
        if asset.retention_days > 730:  # 2 years - reasonable for most data
            issues.append("Consider shorter retention period for personal information")
        
        # Check if asset has clear ownership (for data access requests)
        if not asset.owner:
            issues.append("Asset should have assigned owner for handling consumer requests")
        
        compliant = len(issues) == 0
        
        return {
            "regulation": "CCPA",
            "asset_id": asset_id,
            "compliant": compliant,
            "issues": issues,
            "classification": asset.classification.value,
            "encrypted": asset.encrypted
        }
    
    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate a privacy compliance report"""
        total_assets = len(self.data_assets)
        encrypted_count = sum(1 for a in self.data_assets.values() if a.encrypted)
        
        classification_dist = {}
        for asset in self.data_assets.values():
            cls = asset.classification.value
            classification_dist[cls] = classification_dist.get(cls, 0) + 1
        
        # Check GDPR compliance for all assets
        gdpr_compliant = sum(
            1 for asset_id in self.data_assets.keys()
            if self.check_gdpr_compliance(asset_id)["compliant"]
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_assets": total_assets,
            "encrypted_assets": encrypted_count,
            "encryption_rate": encrypted_count / total_assets if total_assets > 0 else 0,
            "classification_distribution": classification_dist,
            "gdpr_compliant_assets": gdpr_compliant,
            "gdpr_compliance_rate": gdpr_compliant / total_assets if total_assets > 0 else 0,
            "audit_log_entries": len(self.audit_log),
            "regulations": [r.value for r in self.compliance_regulations]
        }
    
    def _log_audit(
        self,
        action: str,
        success: bool,
        user_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an audit entry"""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            action=action,
            user_id=user_id,
            asset_id=asset_id,
            success=success,
            details=details or {}
        )
        
        self.audit_log.append(entry)
    
    def get_audit_log(
        self,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        entries = self.audit_log
        
        if action:
            entries = [e for e in entries if e.action == action]
        
        entries = entries[-limit:]
        
        return [
            {
                "timestamp": entry.timestamp.isoformat(),
                "action": entry.action,
                "user_id": entry.user_id,
                "asset_id": entry.asset_id,
                "success": entry.success,
                "details": entry.details
            }
            for entry in entries
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get security manager statistics"""
        return {
            "total_assets": len(self.data_assets),
            "encrypted_assets": sum(1 for a in self.data_assets.values() if a.encrypted),
            "audit_log_size": len(self.audit_log),
            "encryption_keys": len(self._encryption_keys),
            "compliance_regulations": [r.value for r in self.compliance_regulations]
        }

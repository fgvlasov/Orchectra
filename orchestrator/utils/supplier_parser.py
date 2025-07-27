"""
Data parsers for supplier information.
"""

import pandas as pd
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..utils.logging import logger


class SupplierDataParser:
    """Parser for supplier data files."""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.json', '.xlsx']
    
    def parse_suppliers(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse supplier data from various file formats."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Supplier file not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        try:
            if file_extension == '.csv':
                return self._parse_csv(file_path)
            elif file_extension == '.json':
                return self._parse_json(file_path)
            elif file_extension == '.xlsx':
                return self._parse_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error parsing supplier file {file_path}: {e}")
            raise
    
    def _parse_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse CSV supplier data."""
        try:
            df = pd.read_csv(file_path)
            suppliers = df.to_dict('records')
            
            # Validate required fields
            required_fields = ['id', 'name', 'country', 'industry']
            missing_fields = [field for field in required_fields if field not in df.columns]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Clean and validate data
            suppliers = self._clean_supplier_data(suppliers)
            
            logger.info(f"Successfully parsed {len(suppliers)} suppliers from CSV")
            return suppliers
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise
    
    def _parse_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse JSON supplier data."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                suppliers = data
            elif isinstance(data, dict) and 'suppliers' in data:
                suppliers = data['suppliers']
            else:
                raise ValueError("Invalid JSON structure for supplier data")
            
            # Validate required fields
            if suppliers and not all('id' in supplier and 'name' in supplier for supplier in suppliers):
                raise ValueError("Missing required fields in JSON data")
            
            # Clean and validate data
            suppliers = self._clean_supplier_data(suppliers)
            
            logger.info(f"Successfully parsed {len(suppliers)} suppliers from JSON")
            return suppliers
            
        except Exception as e:
            logger.error(f"Error parsing JSON file: {e}")
            raise
    
    def _parse_excel(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Excel supplier data."""
        try:
            df = pd.read_excel(file_path)
            suppliers = df.to_dict('records')
            
            # Validate required fields
            required_fields = ['id', 'name', 'country', 'industry']
            missing_fields = [field for field in required_fields if field not in df.columns]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            # Clean and validate data
            suppliers = self._clean_supplier_data(suppliers)
            
            logger.info(f"Successfully parsed {len(suppliers)} suppliers from Excel")
            return suppliers
            
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            raise
    
    def _clean_supplier_data(self, suppliers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate supplier data."""
        cleaned_suppliers = []
        
        for supplier in suppliers:
            try:
                cleaned_supplier = self._clean_single_supplier(supplier)
                if cleaned_supplier:
                    cleaned_suppliers.append(cleaned_supplier)
            except Exception as e:
                logger.warning(f"Error cleaning supplier {supplier.get('id', 'unknown')}: {e}")
                continue
        
        return cleaned_suppliers
    
    def _clean_single_supplier(self, supplier: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean a single supplier record."""
        # Ensure required fields exist
        if not supplier.get('id') or not supplier.get('name'):
            return None
        
        # Clean and standardize fields
        cleaned = {
            'id': str(supplier['id']).strip(),
            'name': str(supplier['name']).strip(),
            'country': str(supplier.get('country', '')).strip(),
            'industry': str(supplier.get('industry', '')).strip(),
            'supplier_type': str(supplier.get('supplier_type', 'Tier 2')).strip(),
            'supply_category': str(supplier.get('supply_category', '')).strip(),
            'esg_score': self._parse_float(supplier.get('esg_score', 0.5)),
            'financial_stability': self._parse_float(supplier.get('financial_stability', 0.5)),
            'prior_violations': self._parse_int(supplier.get('prior_violations', 0)),
            'annual_spend': self._parse_float(supplier.get('annual_spend', 0)),
            'contract_duration': self._parse_int(supplier.get('contract_duration', 1)),
            'risk_level': str(supplier.get('risk_level', 'medium')).strip().lower()
        }
        
        # Validate numeric ranges
        cleaned['esg_score'] = max(0.0, min(1.0, cleaned['esg_score']))
        cleaned['financial_stability'] = max(0.0, min(1.0, cleaned['financial_stability']))
        cleaned['prior_violations'] = max(0, cleaned['prior_violations'])
        cleaned['annual_spend'] = max(0.0, cleaned['annual_spend'])
        cleaned['contract_duration'] = max(1, cleaned['contract_duration'])
        
        # Validate risk level
        valid_risk_levels = ['low', 'medium', 'high', 'critical']
        if cleaned['risk_level'] not in valid_risk_levels:
            cleaned['risk_level'] = 'medium'
        
        return cleaned
    
    def _parse_float(self, value: Any) -> float:
        """Parse float value with error handling."""
        try:
            if value is None or value == '':
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_int(self, value: Any) -> int:
        """Parse integer value with error handling."""
        try:
            if value is None or value == '':
                return 0
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def validate_supplier_data(self, suppliers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate supplier data and return statistics."""
        if not suppliers:
            return {
                'valid': False,
                'total_suppliers': 0,
                'errors': ['No suppliers found']
            }
        
        validation_results = {
            'valid': True,
            'total_suppliers': len(suppliers),
            'countries': set(),
            'industries': set(),
            'supplier_types': set(),
            'risk_levels': set(),
            'errors': [],
            'warnings': []
        }
        
        for supplier in suppliers:
            # Collect statistics
            validation_results['countries'].add(supplier.get('country', ''))
            validation_results['industries'].add(supplier.get('industry', ''))
            validation_results['supplier_types'].add(supplier.get('supplier_type', ''))
            validation_results['risk_levels'].add(supplier.get('risk_level', ''))
            
            # Validate individual supplier
            supplier_errors = self._validate_single_supplier(supplier)
            if supplier_errors:
                validation_results['errors'].extend(supplier_errors)
                validation_results['valid'] = False
        
        # Convert sets to lists for JSON serialization
        validation_results['countries'] = list(validation_results['countries'])
        validation_results['industries'] = list(validation_results['industries'])
        validation_results['supplier_types'] = list(validation_results['supplier_types'])
        validation_results['risk_levels'] = list(validation_results['risk_levels'])
        
        return validation_results
    
    def _validate_single_supplier(self, supplier: Dict[str, Any]) -> List[str]:
        """Validate a single supplier record."""
        errors = []
        
        # Check required fields
        if not supplier.get('id'):
            errors.append(f"Missing supplier ID")
        if not supplier.get('name'):
            errors.append(f"Missing supplier name")
        if not supplier.get('country'):
            errors.append(f"Missing country for supplier {supplier.get('id', 'unknown')}")
        if not supplier.get('industry'):
            errors.append(f"Missing industry for supplier {supplier.get('id', 'unknown')}")
        
        # Check numeric ranges
        if supplier.get('esg_score', 0) < 0 or supplier.get('esg_score', 0) > 1:
            errors.append(f"Invalid ESG score for supplier {supplier.get('id', 'unknown')}")
        if supplier.get('financial_stability', 0) < 0 or supplier.get('financial_stability', 0) > 1:
            errors.append(f"Invalid financial stability for supplier {supplier.get('id', 'unknown')}")
        
        return errors


class ExternalDataParser:
    """Parser for external ESG and compliance data."""
    
    def __init__(self):
        self.supported_formats = ['.json', '.csv', '.xml']
    
    def parse_sanction_lists(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse sanction lists from various formats."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Sanction list file not found: {file_path}")
            return []
        
        try:
            if file_path.suffix.lower() == '.json':
                return self._parse_json_sanctions(file_path)
            elif file_path.suffix.lower() == '.csv':
                return self._parse_csv_sanctions(file_path)
            else:
                logger.warning(f"Unsupported sanction list format: {file_path.suffix}")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing sanction list {file_path}: {e}")
            return []
    
    def _parse_json_sanctions(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse JSON sanction list."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'sanctions' in data:
                return data['sanctions']
            else:
                logger.warning(f"Invalid JSON structure for sanctions: {file_path}")
                return []
                
        except Exception as e:
            logger.error(f"Error parsing JSON sanctions: {e}")
            return []
    
    def _parse_csv_sanctions(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse CSV sanction list."""
        try:
            df = pd.read_csv(file_path)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error parsing CSV sanctions: {e}")
            return []
    
    def parse_violation_database(self, file_path: str) -> Dict[str, List[str]]:
        """Parse violation database."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Violation database file not found: {file_path}")
            return {}
        
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Unsupported violation database format: {file_path.suffix}")
                return {}
                
        except Exception as e:
            logger.error(f"Error parsing violation database: {e}")
            return {} 
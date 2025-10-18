from aivia.matching.faiss_search import load_faiss_handles
from typing import Dict, Any
from aivia.extras.config import get_pattern_registry
from aivia.pathfinder.engine import get_pathfinder_engine

def _extract_needs(entities, filters=None) -> Dict[str, Any]:
    """Extract conditions and time windows from entities and filters safely."""
    conditions = []
    time_windows = []
    
    if not entities:
        entities = []
    if not filters:
        filters = []

    for entity in entities:
        if entity is None:
            continue
            
        entity_type = getattr(entity, 'type', None)
        if entity_type == "condition":
            normalized = getattr(entity, 'normalized', None) or {}
            if normalized:
                conditions.append(normalized)
            else:
                mention = getattr(entity, 'mention', '')
                if mention:
                    conditions.append({"condition_text": mention})
        elif entity_type == "time_window":
            normalized = getattr(entity, 'normalized', None) or {}
            if normalized:
                time_windows.append(normalized)
            else:
                mention = getattr(entity, 'mention', '')
                if mention:
                    time_windows.append({"time_text": mention})

    return {
        "conditions": conditions,
        "time_windows": time_windows
    }

def _schema_based_token_matching(entities, clarity_schema):
    """Schema-driven token matching using table names and column patterns."""
    entity_tokens = []
    value_tokens = []
    time_windows = []
    negation_patterns = []
    
    for entity in entities:
        mention = getattr(entity, 'mention', '')
        entity_type = getattr(entity, 'type', '')
        
        if entity_type in ['entity', 'location', 'provider', 'attribute']:
            entity_tokens.append(mention)
        elif entity_type in ['value', 'condition']:
            value_tokens.append(mention)
        elif entity_type == 'time_window':
            time_windows.append(mention)
        elif entity_type == 'negation':
            negation_patterns.append(mention)
            print(f"🚫 Negation detected: '{mention}'")
    
    print(f"🔍 SCHEMA-BASED MATCHING - Entity tokens: {entity_tokens}")
    print(f"🔍 SCHEMA-BASED MATCHING - Value tokens: {value_tokens}")
    
    # Generic entity→table matching using schema
    entity_matches = []
    if clarity_schema and 'tables' in clarity_schema:
        for token in entity_tokens:
            for table_name, table_info in clarity_schema['tables'].items():
                # Generic similarity matching
                if _token_matches_table(token, table_name, table_info):
                    entity_matches.append({
                        'table': table_name, 
                        'score': 0.9, 
                        'type': 'table'
                    })
                    break  # Take first match
    
    # Context-aware value→category matching using schema  
    value_matches = []
    if clarity_schema and 'tables' in clarity_schema:
        for token in value_tokens:
            # Use existing dynamic medical concept detection with flexible matching
            registry = get_pattern_registry()
            medical_concept = registry.find_medical_concept(token)
            
            # If direct lookup fails, try common variations
            if not medical_concept:
                medical_concept = _find_medical_concept_with_variations(registry, token)
            
            print(f"🔍 Medical concept lookup for '{token}': {medical_concept}")
            
            # Path 1: Medical Conditions → Diagnosis Tables
            if medical_concept:
                # Dynamically find diagnosis tables and columns from schema
                diagnosis_table, diagnosis_column = _find_diagnosis_table_and_column(clarity_schema)
                print(f"🔍 Diagnosis table discovery: table={diagnosis_table}, column={diagnosis_column}")
                if diagnosis_table and diagnosis_column:
                    # Use the medical concept's preferred term for search
                    search_term = medical_concept.preferred_term
                    value_matches.append({
                        'table': diagnosis_table,
                        'column': diagnosis_column, 
                        'value': search_term,
                        'score': 0.95,
                        'type': 'diagnosis'
                    })
                    print(f"🏥 Medical condition match: '{token}' → {diagnosis_table}.{diagnosis_column} LIKE '%{search_term}%'")
            
            # Path 2: Status Values → Category Tables (parallel, not fallback)
            else:
                # Check if this token represents a status value
                matched_value = _token_to_category_value(token)
                if matched_value:
                    # Find the most appropriate ZC_ table based on context
                    best_table = _find_best_category_table(token, entity_tokens, clarity_schema)
                    if best_table:
                        value_matches.append({
                            'table': best_table,
                            'column': 'NAME', 
                            'value': matched_value,
                            'score': 0.95,
                            'type': 'category_value'
                        })
                        print(f"📋 Status value match: '{token}' → {best_table}.NAME = '{matched_value}'")
    
    # Process negation patterns
    negation_filters = []
    for negation in negation_patterns:
        # Extract the negated concept (e.g., "no appointment" → "appointment")
        negated_concept = _extract_negated_concept(negation)
        if negated_concept:
            # Find which table this concept relates to
            negated_table = _find_table_for_concept(negated_concept, clarity_schema)
            if negated_table:
                negation_filters.append({
                    'concept': negated_concept,
                    'table': negated_table,
                    'pattern': negation,
                    'type': 'not_exists'
                })
                print(f"🚫 Negation filter: '{negation}' → NOT EXISTS {negated_table}")
    
    return entity_matches, value_matches, time_windows, negation_filters

def _token_matches_table(token, table_name, table_info):
    """Generic token→table matching using schema aliases."""
    token_lower = token.lower()
    table_lower = table_name.lower()
    
    # Check if table_info has aliases (schema-driven matching)
    if isinstance(table_info, dict) and 'aliases' in table_info:
        aliases = table_info['aliases']
        for alias in aliases:
            if token_lower in alias.lower() or alias.lower() in token_lower:
                return True
    
    # Fallback: direct table name matching
    if token_lower in table_lower or table_lower in token_lower:
        return True
        
    return False


def _token_to_category_value(token):
    """Generic token→category value mapping using capitalization patterns."""
    if not token:
        return None

    # Handle multi-word statuses
    if ' ' in token:
        return ' '.join(word.capitalize() for word in token.split())
    
    # Simple capitalization - most category values follow this pattern
    return token.capitalize()

def _extract_negated_concept(negation_text):
    """Extract the negated concept from negation patterns."""
    negation_lower = negation_text.lower()
    
    # Common negation patterns
    if negation_lower.startswith('no '):
        concept = negation_text[3:].strip()  # "no appointment" → "appointment"
    elif negation_lower.startswith('without '):
        concept = negation_text[8:].strip()  # "without visits" → "visits"
    elif negation_lower.startswith('missing '):
        concept = negation_text[8:].strip()  # "missing referral" → "referral"
    elif negation_lower.startswith('not '):
        concept = negation_text[4:].strip()  # "not scheduled" → "scheduled"
    else:
        return None
    
    # Use dynamic pattern registry to normalize concepts
    registry = get_pattern_registry()
    
    # Get entity types from configuration
    entity_types = registry.get_entity_types()
    
    concept_lower = concept.lower()
    
    # Check against semantic indicators from configuration
    for entity_type, config in entity_types.items():
        for indicator in config.semantic_indicators:
            if indicator in concept_lower:
                return indicator
    
    return concept

def _find_table_for_concept(concept, clarity_schema):
    """Find the most appropriate table for a concept."""
    if not clarity_schema or 'tables' not in clarity_schema:
        return None

    concept_lower = concept.lower()
    
    # Use dynamic pattern registry for concept-to-table mapping
    registry = get_pattern_registry()
    
    # Discover entity types from schema dynamically
    discovered_entities = registry.discover_entities_from_schema(clarity_schema)
    
    # Build dynamic concept-to-table mapping
    concept_table_map = {}
    for table_name, table_info in clarity_schema['tables'].items():
        column_names = []
        if 'columns_priority' in table_info:
            column_names = [col.get('name', '') for col in table_info['columns_priority']]
        
        entity_type = registry.find_entity_type_from_schema(table_name, column_names)
        if entity_type:
            # Map semantic indicators to this table
            indicators = registry.get_semantic_indicators(entity_type)
            for indicator in indicators:
                concept_table_map[indicator] = table_name
                concept_table_map[indicator + 's'] = table_name  # Plural form
    
    if concept_lower in concept_table_map:
        return concept_table_map[concept_lower]
    
    # Fallback: search aliases in schema
    for table_name, table_info in clarity_schema['tables'].items():
        if 'aliases' in table_info:
            for alias in table_info['aliases']:
                if concept_lower in alias.lower() or alias.lower() in concept_lower:
                    return table_name
    
    return None

def _get_primary_key(table_name, clarity_schema):
    """Get the primary key column for a table."""
    if not clarity_schema or 'tables' not in clarity_schema:
        return 'ID'  # Default fallback
    
    table_info = clarity_schema['tables'].get(table_name, {})
    
    # Check if primary_key is explicitly defined
    if 'primary_key' in table_info:
        return table_info['primary_key']
    
    # Common primary key patterns
    pk_patterns = {
        'PAT_ENC': 'PAT_ENC_CSN_ID',
        'REFERRAL': 'REFERRAL_ID',
        'PATIENT': 'PAT_ID',
        'CLARITY_SER': 'PROV_ID'
    }
    
    if table_name in pk_patterns:
        return pk_patterns[table_name]
    
    # Fallback: look for ID-like columns
    if 'columns_priority' in table_info:
        for col in table_info['columns_priority']:
            col_name = col.get('name', '')
            if col_name.endswith('_ID') or col_name == 'ID':
                return col_name
    
    return 'ID'  # Ultimate fallback

def _find_medical_concept_with_variations(registry, token):
    """Find medical concept using dynamic linguistic variations."""
    token_lower = token.lower()
    
    # Get all available medical concepts to search through
    all_concepts = getattr(registry, '_medical_concepts', {})
    
    # Strategy 1: Fuzzy matching - check if token is contained in any concept terms
    for concept in all_concepts.values():
        # Check if token is a substring of preferred term or synonyms
        preferred_lower = concept.preferred_term.lower()
        if token_lower in preferred_lower or preferred_lower in token_lower:
            return concept
        
        for synonym in concept.synonyms:
            synonym_lower = synonym.lower()
            if token_lower in synonym_lower or synonym_lower in token_lower:
                return concept
    
    # Strategy 2: Morphological variations - try removing/adding common medical suffixes
    medical_suffixes = ['ic', 'tic', 'al', 'ous', 'ive', 'ism', 'osis', 'itis', 'emia', 'uria']
    
    # Try removing suffixes from token
    for suffix in medical_suffixes:
        if token_lower.endswith(suffix) and len(token_lower) > len(suffix) + 2:
            stem = token_lower[:-len(suffix)]
            # Search for concepts containing this stem
            for concept in all_concepts.values():
                preferred_lower = concept.preferred_term.lower()
                if stem in preferred_lower:
                    return concept
                for synonym in concept.synonyms:
                    if stem in synonym.lower():
                        return concept
    
    # Try adding suffixes to token
    for suffix in medical_suffixes:
        variant = token_lower + suffix
        for concept in all_concepts.values():
            preferred_lower = concept.preferred_term.lower()
            if variant in preferred_lower or preferred_lower in variant:
                return concept
            for synonym in concept.synonyms:
                synonym_lower = synonym.lower()
                if variant in synonym_lower or synonym_lower in variant:
                    return concept
    
    return None


def _find_diagnosis_table_and_column(clarity_schema):
    """Dynamically discover diagnosis table and column using schema relationships and descriptions."""
    if not clarity_schema or 'tables' not in clarity_schema:
        return None, None
    
    # Strategy: Find tables whose descriptions mention diagnosis-related terms
    # Then find columns in those tables that likely contain searchable text
    
    diagnosis_keywords = ['diagnosis', 'diagnostic', 'condition', 'disease', 'medical', 'clinical']
    text_column_indicators = ['name', 'desc', 'description', 'text', 'title', 'label']
    
    candidates = []
    
    # Score tables based on how likely they are to contain diagnosis information
    for table_name, table_info in clarity_schema['tables'].items():
        description = table_info.get('description', '').lower()
        aliases = [alias.lower() for alias in table_info.get('aliases', [])]
        
        # Calculate diagnosis relevance score
        diagnosis_score = 0
        for keyword in diagnosis_keywords:
            if keyword in description:
                diagnosis_score += 2
            for alias in aliases:
                if keyword in alias:
                    diagnosis_score += 1
        
        # Look for text columns in this table
        columns = table_info.get('columns_priority', [])
        for col in columns:
            col_name = col.get('name', '').lower()
            col_desc = col.get('description', '').lower()
            
            # Calculate text column score
            text_score = 0
            for indicator in text_column_indicators:
                if indicator in col_name:
                    text_score += 2
                if indicator in col_desc:
                    text_score += 1
            
            # Combined score
            total_score = diagnosis_score + text_score
            if total_score > 0:
                candidates.append({
                    'table': table_name,
                    'column': col['name'],
                    'score': total_score,
                    'reason': f"diagnosis_score={diagnosis_score}, text_score={text_score}"
                })
    
    # Sort by score and return the best candidate
    if candidates:
        best = max(candidates, key=lambda x: x['score'])
        print(f"🔍 Dynamic diagnosis discovery: {best['table']}.{best['column']} (score={best['score']}, {best['reason']})")
        return best['table'], best['column']
    
    print("🔍 No diagnosis table/column found through dynamic discovery")
    return None, None


def _find_best_category_table(value_token, entity_tokens, clarity_schema):
    """Find the most appropriate ZC_ category table based on schema relationships and semantic context."""
    if not clarity_schema or 'tables' not in clarity_schema:
        return None
    
    # Get all available ZC_ tables with NAME columns
    available_zc_tables = []
    for table_name, table_info in clarity_schema['tables'].items():
        if table_name.startswith('ZC_') and 'columns_priority' in table_info:
            column_names = [col['name'] for col in table_info['columns_priority']]
            if 'NAME' in column_names:
                available_zc_tables.append(table_name)
    
    if not available_zc_tables:
        return None
    
    # Semantic-based category table selection for specific status values
    value_lower = value_token.lower()
    
    # Use dynamic pattern registry for status matching
    registry = get_pattern_registry()
    
    # Find entity types that might have status values
    entity_types = registry.get_entity_types()
    
    for entity_type, config in entity_types.items():
        # Check if this value relates to this entity type
        for indicator in config.semantic_indicators:
            if indicator in value_lower or any(indicator in word for word in value_lower.split()):
                # Look for corresponding ZC_ table
                possible_zc_tables = [table for table in available_zc_tables 
                                    if any(pattern.replace('*', '').upper() in table 
                                          for pattern in config.table_patterns)]
                if possible_zc_tables:
                    best_table = possible_zc_tables[0]  # Take first match
                    print(f"🎯 Dynamic semantic match: '{value_token}' → {best_table} ({entity_type})")
                    return best_table
    
    # Referral-specific statuses  
    referral_statuses = ['open', 'closed', 'declined', 'in progress']
    if any(status in value_lower for status in referral_statuses):
        if 'ZC_REFERRAL_STATUS' in available_zc_tables:
            print(f"🎯 Semantic match: '{value_token}' → ZC_REFERRAL_STATUS (referral status)")
            return 'ZC_REFERRAL_STATUS'
    
    # Use schema relationships to find the best match
    # Look for ZC_ tables that are connected to entity tables in the schema joins
    if 'joins' in clarity_schema:
        entity_tables = []
        for token in entity_tokens:
            # Find which main tables this entity token matches
            for table_name, table_info in clarity_schema['tables'].items():
                if not table_name.startswith('ZC_') and _token_matches_table(token, table_name, table_info):
                    entity_tables.append(table_name)
        
        # Find ZC_ tables that join to these entity tables
        for join in clarity_schema['joins']:
            left_table = join.get('left_table', '')
            right_table = join.get('right_table', '')
            
            # Check if any entity table joins to a ZC_ table
            for entity_table in entity_tables:
                if ((left_table == entity_table and right_table in available_zc_tables) or
                    (right_table == entity_table and left_table in available_zc_tables)):
                    return right_table if left_table == entity_table else left_table
    
    # Fallback: return first available ZC_ table
    return available_zc_tables[0] if available_zc_tables else None

def load_indexes(faiss_config):
    """Load FAISS indexes with error handling."""
    try:
        return load_faiss_handles(faiss_config)
    except Exception as e:
        print(f"[WARNING] FAISS loading failed: {e}")
    return None

def match_labels_and_filters(*, question, target_row_grain, entities, filters, faiss_config, clarity_schema):
    """Main matching function with enhanced token-based approach."""
    print(f"🔍 MATCHER DEBUG - Question: '{question}'")
    print(f"🔍 MATCHER DEBUG - Entities received: {len(entities)}")
    for i, entity in enumerate(entities):
        print(f"   {i+1}. '{getattr(entity, 'mention', 'NO_MENTION')}' type='{getattr(entity, 'type', 'NO_TYPE')}'")
    
    # Try to load FAISS, but continue gracefully if it fails
        handles = load_indexes(faiss_config)
    
    if handles:
        print("✅ FAISS handles loaded successfully")
        # TODO: Use real FAISS matching when indexes are fixed
        entity_matches, value_matches, time_windows, negation_filters = _schema_based_token_matching(entities, clarity_schema)
    else:
        print("🔄 Using schema-based matching due to FAISS issues")
        entity_matches, value_matches, time_windows, negation_filters = _schema_based_token_matching(entities, clarity_schema)
    
    print(f"🔍 ENHANCED MATCHING - Entity matches: {len(entity_matches)}")
    for match in entity_matches:
        print(f"   Entity: '{match['table']}' (score: {match['score']:.3f})")
    
    print(f"🔍 ENHANCED MATCHING - Value matches: {len(value_matches)}")  
    for match in value_matches:
        print(f"   Value: {match['table']}.{match['column']} = '{match['value']}' (score: {match['score']:.3f})")
    
    print(f"🔍 ENHANCED MATCHING - Time windows: {len(time_windows)}")
    for tw in time_windows:
        print(f"   Time window: '{tw}'")
    
    print(f"🔍 ENHANCED MATCHING - Negation filters: {len(negation_filters)}")
    for nf in negation_filters:
        print(f"   Negation: '{nf['pattern']}' → NOT EXISTS {nf['table']}")
    
    # Process time windows into temporal filters
    temporal_filters = []
    if time_windows:
        try:
            from aivia.nl.parse.time import parse_calendar_window
            import datetime as dt
            
            for tw in time_windows:
                # Use a simple "now" function for testing
                now_func = lambda: dt.date.today()
                parsed_window = parse_calendar_window(tw, now=now_func)
                
                if parsed_window:
                    # Create a temporal filter in the format expected by SQL builder
                    temporal_filter = {
                        'kind': 'time_range',
                        'applies_to': [],  # Will be set based on the main table
                        'source': 'time_window_entity'
                    }
                    
                    # Convert parsed window to SQL builder format
                    if 'rel' in parsed_window:
                        # Relative format: {"rel": {"unit": "month", "value": -1}}
                        temporal_filter['start'] = parsed_window
                        temporal_filter['end'] = "NOW"
                    elif 'abs' in parsed_window and len(parsed_window['abs']) == 2:
                        # Absolute format: {"abs": ["2025-08-01", "2025-08-31"]}
                        # Convert to relative format for SQL builder compatibility
                        temporal_filter['start'] = {"relative": {"unit": "month", "value": 1, "direction": "past"}}
                        temporal_filter['end'] = "NOW"
                    
                    temporal_filters.append(temporal_filter)
                    print(f"   → Parsed temporal filter: {parsed_window}")
        except Exception as e:
            print(f"   [WARNING] Temporal parsing failed: {e}")
    
    if entity_matches or value_matches or negation_filters:
        # Determine main table intelligently - prioritize target grain
        if entity_matches:
            # First check if target grain matches any entity
            target_table = target_row_grain.upper() if target_row_grain else None
            if target_table and any(match['table'] == target_table for match in entity_matches):
                from_table = target_table
                print(f"🎯 Main table: {from_table} (matches target grain {target_row_grain})")
                # Plan joins for all other entity matches
                other_entity_tables = [match['table'] for match in entity_matches if match['table'] != from_table]
            else:
                # Fallback to first entity match
                from_table = entity_matches[0]['table']
                print(f"🎯 Main table: {from_table} (from {len(entity_matches)} entity matches)")
                # Plan joins for other entity matches
                other_entity_tables = [match['table'] for match in entity_matches[1:]]
            
            if other_entity_tables:
                print(f"🔗 Additional entity tables to join: {other_entity_tables}")
        elif value_matches:
            # Use LLM's target_row_grain instead of hardcoded fallbacks
            if target_row_grain and target_row_grain.upper() in ['REFERRAL', 'PATIENT', 'ENCOUNTER', 'APPOINTMENT', 'PROVIDER', 'DEPARTMENT']:
                from_table = target_row_grain.upper()
                print(f"🎯 Main table: {from_table} (from LLM target_row_grain)")
            else:
                # Only if target_row_grain is invalid, use PATIENT as last resort
                from_table = "PATIENT"
                print(f"🎯 Main table: {from_table} (default - invalid target_row_grain: {target_row_grain})")
        elif negation_filters:
            # For pure negation queries, use the most appropriate main table
            from_table = target_row_grain.upper() if target_row_grain.upper() in ['REFERRAL', 'PATIENT', 'ENCOUNTER'] else "PATIENT"
            print(f"🎯 Main table for negation: {from_table}")
        else:
            from_table = "PATIENT"
        
        # Create joins using existing join planner
        joins = []
        
        # Collect all tables that need to be joined (deduplicated)
        tables_to_join = set()
        
        # Add entity tables (except main table)
        if entity_matches:
            for match in entity_matches:
                if match['table'] != from_table:
                    tables_to_join.add(match['table'])
        
        # Add value match tables (except main table)
        if value_matches:
            for value_match in value_matches:
                if value_match['table'] != from_table:
                    tables_to_join.add(value_match['table'])
        
        # Plan joins using unified PathfinderEngine (Phase B: 3-layer architecture)
        if tables_to_join:
            try:
                print(f"🔍 TABLES TO JOIN: {from_table} -> {list(tables_to_join)}")
                
                # Convert tables to PathfinderEngine target format
                targets = []
                for table in tables_to_join:
                    # Find columns needed for this table from value_matches
                    columns = []
                    for value_match in value_matches:
                        if value_match.get('table') == table:
                            column = value_match.get('column')
                            if column and column not in columns:
                                columns.append(column)
                    
                    targets.append({
                        "table": table,
                        "columns": columns or ["*"]  # Default to all columns if none specified
                    })
                
                # Use unified PathfinderEngine - single source of truth
                engine = get_pathfinder_engine()
                path_plan = engine.complete_path(row_grain=from_table, targets=targets)
                
                # Convert PathPlan to legacy format for SQL generation compatibility
                neo4j_plan = {
                    "nodes": path_plan.nodes,
                    "edges": [[edge[0], edge[1]] for edge in path_plan.edges],
                    "edges_on": path_plan.edges_on,
                    "metadata": {
                        "resolver": path_plan.resolver,
                        "explanation": path_plan.explanation or [],
                        "cost": path_plan.cost
                    }
                }
                
                # Convert Neo4j plan to join format expected by matcher
                path_joins = []
                for edge in neo4j_plan.get("edges", []):
                    if len(edge) == 2:
                        source_table, target_table = edge
                        edge_key = f"{source_table}->{target_table}"
                        join_clause = neo4j_plan.get("edges_on", {}).get(edge_key)
                        if not join_clause:
                            print(f"⚠️  WARNING: No join condition found for {edge_key}")
                            print(f"    Available keys: {list(neo4j_plan.get('edges_on', {}).keys())}")
                            join_clause = f"{target_table}.ID = {source_table}.ID"
                            print(f"    Using fallback: {join_clause}")
                        else:
                            print(f"✅ Found join condition for {edge_key}: {join_clause}")
                        path_joins.append({
                            "source_table": source_table,
                            "target_table": target_table,
                            "join_clause": join_clause,
                            "join_type": "INNER"
                        })
                
                joins.extend(path_joins)
                resolver_type = neo4j_plan.get("metadata", {}).get("resolver", "neo4j")
                print(f"🔗 Neo4j planned joins for tables {list(tables_to_join)}: {len(path_joins)} joins (resolver: {resolver_type})")
            except Exception as e:
                print(f"[WARNING] Neo4j join planning failed: {e}")
                # No fallback - force proper path finding
        
        # Create filters in the format expected by SQL builder
        matched_filters = []
        for match in value_matches:
            matched_filters.append({
                'type': 'Codeset',  # Use the correct type expected by SQL orchestrator
                'table': match['table'],
                'column': match['column'],
                'operator': 'IN',
                'values': [match['value']],
                'confidence': match['score']
            })
        
        # Add temporal filters with appropriate column
        for tf in temporal_filters:
            # Set the appropriate date column based on the main table
            if from_table == 'PAT_ENC':
                tf['applies_to'] = ['PAT_ENC.CONTACT_DATE']
            elif from_table == 'REFERRAL':
                tf['applies_to'] = ['REFERRAL.REFERRAL_DATE']
            else:
                tf['applies_to'] = [f'{from_table}.CONTACT_DATE']  # Default
            
            matched_filters.append(tf)
        
        # Add negation filters
        for nf in negation_filters:
            negation_table = nf['table']
            
            # Plan LEFT JOIN for negation using Neo4j-based path finding
            if negation_table != from_table:
                try:
                    # Build full plan structure for Neo4j resolver
                    all_tables = [from_table, negation_table]
                    full_plan = {
                        "nodes": all_tables,
                        "edges": [],  # Neo4j will discover optimal edges
                        "edges_on": {}
                    }
                    
                    # Use PathfinderEngine for negation path planning
                    engine = get_pathfinder_engine()
                    targets = [{"table": negation_table, "columns": ["*"]}]
                    path_plan = engine.complete_path(from_table, targets)
                    
                    # Convert PathPlan to legacy format for compatibility
                    neo4j_plan = {
                        "nodes": path_plan.nodes,
                        "edges": [[edge[0], edge[1]] for edge in path_plan.edges],
                        "edges_on": path_plan.edges_on
                    }
                    
                    # Convert Neo4j plan to LEFT JOIN format for negation
                    negation_joins = []
                    for edge in neo4j_plan.get("edges", []):
                        if len(edge) == 2:
                            source_table, target_table = edge
                            join_clause = neo4j_plan.get("edges_on", {}).get(f"{source_table}->{target_table}", 
                                                                            f"{target_table}.ID = {source_table}.ID")
                            negation_joins.append({
                                "source_table": source_table,
                                "target_table": target_table,
                                "join_clause": join_clause,
                                "join_type": "LEFT"  # LEFT JOIN for negation logic
                            })
                    
                    joins.extend(negation_joins)
                    resolver_type = neo4j_plan.get("metadata", {}).get("resolver", "neo4j")
                    print(f"🔗 Neo4j planned LEFT JOINs for negation {negation_table}: {len(negation_joins)} joins (resolver: {resolver_type})")
                except Exception as e:
                    print(f"[WARNING] Neo4j negation join planning failed: {e}")
                    # No fallback - force proper path finding
            
            # Create negation filter (IS NULL check)
            negation_filter = {
                'kind': 'negation_filter',
                'applies_to': [f'{negation_table}.{_get_primary_key(negation_table, clarity_schema)}'],
                'operator': 'IS NULL',
                'source': 'negation_pattern',
                'pattern': nf['pattern']
            }
            matched_filters.append(negation_filter)
            print(f"🚫 Added negation filter: {negation_filter['applies_to'][0]} IS NULL")
        
        # Use from_table as row_grain (no hardcoded overrides)
        row_grain = from_table
        
        # Create select clause dynamically based on table
        if from_table == "PAT_ENC":
            primary_key = "PAT_ENC_CSN_ID"
            alias = "PAT_ENC_ID"
        elif from_table == "REFERRAL":
            primary_key = "REFERRAL_ID"
            alias = "REFERRAL_ID"
        elif from_table == "PATIENT":
            primary_key = "PAT_ID"
            alias = "PATIENT_ID"
        else:
            # Generic pattern for other tables
            primary_key = f"{from_table}_ID"
            alias = f"{from_table}_ID"
        
        result = {
            "distinct": True,
            "from": from_table,
            "row_grain": row_grain,
            "joins": joins,
            "filters": matched_filters,
            "select": [{"table": from_table, "column": primary_key, "alias": alias}],
            "source": "schema-based"
        }
        
        print(f"🎯 ENHANCED RESULT: {from_table} with {len(joins)} joins, {len(matched_filters)} filters")
        return result
    
    # NO FALLBACKS - Fail transparently if we reach this point
    raise RuntimeError(
        "Schema matching failed: No entity matches, value matches, or negation filters found. "
        "This indicates either: "
        "1. LLM entity extraction failed to identify relevant entities "
        "2. Schema matching failed to find appropriate tables "
        "3. Query contains unsupported patterns "
        "No fallback logic - system designed to fail transparently."
    )


def _find_best_category_table(token, entity_tokens, clarity_schema):
    """
    Find the most appropriate ZC_ category table based on context from entity tokens.
    
    Args:
        token: The status value token (e.g., "scheduled", "cancelled")
        entity_tokens: List of entity tokens that provide context (e.g., ["referrals", "appointments"])
        clarity_schema: The schema dictionary with table information
    
    Returns:
        str: The best matching ZC_ table name, or None if no good match found
    """
    if not entity_tokens or not clarity_schema:
        return None
    
    # Convert entity tokens to lowercase for matching
    entity_tokens_lower = [token.lower() for token in entity_tokens]
    
    # Define context-based mapping rules
    table_mappings = {
        # Appointment-related entities
        'ZC_APPT_STATUS': [
            'appointment', 'appointments', 'appt', 'visit', 'visits', 
            'encounter', 'encounters', 'meeting', 'consultation'
        ],
        # Referral-related entities  
        'ZC_RFL_STATUS': [
            'referral', 'referrals', 'refer', 'rfl'
        ],
        # Patient encounter-related (if we had ZC_ENC_STATUS)
        'ZC_ENC_STATUS': [
            'encounter', 'encounters', 'enc', 'admission', 'stay'
        ]
    }
    
    # Score each table based on how well entity tokens match its context
    table_scores = {}
    
    for table_name, context_keywords in table_mappings.items():
        # Check if this table exists in the schema
        if clarity_schema.get('tables', {}).get(table_name):
            score = 0
            
            # Calculate match score based on entity token overlap
            for entity_token in entity_tokens_lower:
                for keyword in context_keywords:
                    if keyword in entity_token or entity_token in keyword:
                        # Exact match gets higher score
                        if keyword == entity_token:
                            score += 10
                        # Partial match gets lower score
                        else:
                            score += 5
            
            # Apply priority boost for appointment-related tables when both appointments and referrals are present
            # This handles cases like "referrals that have scheduled appointments" where "scheduled" should map to appointment status
            if (table_name == 'ZC_APPT_STATUS' and 
                any('appointment' in token for token in entity_tokens_lower) and
                any('referral' in token for token in entity_tokens_lower)):
                score += 15  # Boost appointment table when both contexts are present
                print(f"🎯 Appointment priority boost applied to {table_name}")
            
            if score > 0:
                table_scores[table_name] = score
                print(f"🎯 Category table scoring: {table_name} = {score} (entities: {entity_tokens})")
    
    # Return the highest scoring table
    if table_scores:
        best_table = max(table_scores.keys(), key=lambda k: table_scores[k])
        print(f"🏆 Best category table for '{token}': {best_table} (score: {table_scores[best_table]})")
        return best_table
    
    # Fallback: if no context match, try to infer from token itself
    token_lower = token.lower()
    
    # Some status values are more commonly associated with certain entity types
    token_hints = {
        'scheduled': 'ZC_APPT_STATUS',  # "scheduled" is primarily appointment status
        'cancelled': 'ZC_APPT_STATUS',  # "cancelled" is primarily appointment status  
        'completed': 'ZC_APPT_STATUS',  # "completed" is primarily appointment status
        'no show': 'ZC_APPT_STATUS',    # "no show" is appointment-specific
        'arrived': 'ZC_APPT_STATUS',    # "arrived" is appointment-specific
        'pending': 'ZC_RFL_STATUS',     # "pending" is often referral status
        'approved': 'ZC_RFL_STATUS',    # "approved" is often referral status
        'rejected': 'ZC_RFL_STATUS',    # "rejected" is often referral status
    }
    
    # Check if token has a hint and the suggested table exists
    if token_lower in token_hints:
        suggested_table = token_hints[token_lower]
        if clarity_schema.get('tables', {}).get(suggested_table):
            print(f"💡 Token hint mapping: '{token}' → {suggested_table}")
            return suggested_table
    
    # Final fallback: return first available status table
    available_status_tables = ['ZC_APPT_STATUS', 'ZC_RFL_STATUS', 'ZC_ENC_STATUS']
    for table in available_status_tables:
        if clarity_schema.get('tables', {}).get(table):
            print(f"🔄 Fallback category table: {table}")
            return table
    
    print(f"❌ No suitable category table found for '{token}' with entities {entity_tokens}")
    return None

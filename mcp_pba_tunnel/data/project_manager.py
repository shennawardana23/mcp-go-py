#!/usr/bin/env python3
"""
Refactored MCP Prompt Engineering Data Management
Uses Repository and Service patterns for clean architecture
"""

import logging
import os
from typing import Dict, List, Any, Optional

from .models import PromptTemplate
from .repositories.database import DatabaseConfig, DatabaseOperations
from .repositories.prompt_repository import PromptTemplateRepository
from .services.prompt_service import PromptService as BusinessLogicPromptService
from .services.ai_service import AIService

# Import patterns from the same package
from .patterns import (
    TemplateFactory, PromptTemplate, PromptRenderer, PromptChain, ChainHandler,
    TemplateValidationHandler, TemplateRenderingHandler, AIEnhancementHandler,
    PromptObserver, UsageTracker, CacheInvalidator, PromptService, PromptBuilder
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database operations manager using psycopg native queries"""

    def __init__(self):
        """Initialize database connection pool"""
        DatabaseConfig.get_connection_pool()

    def create_tables(self):
        """Create all database tables"""
        from .repositories.database import DatabaseOperations

        # Create all tables
        self._create_prompt_templates_table()
        self._create_prompt_usage_table()
        self._create_ai_configurations_table()
        self._create_generated_content_table()
        self._create_memory_entries_table()
        self._create_enhanced_memory_entries_table()
        self._create_context_relationships_table()
        self._create_prompt_chains_table()
        self._create_prompt_chain_executions_table()
        logger.info("All database tables created successfully")

    def run_migrations(self):
        """Run database migrations"""
        try:
            # Create migration tracking table if it doesn't exist
            self._create_migration_table()

            # Get list of migration files
            migration_dir = "migrations"
            if not os.path.exists(migration_dir):
                os.makedirs(migration_dir)
                logger.info(f"Created migrations directory: {migration_dir}")

            # Run pending migrations
            self._run_pending_migrations(migration_dir)
            logger.info("Migrations completed successfully")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

    def _create_migration_table(self):
        """Create migration tracking table"""
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(50) PRIMARY KEY,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created migration tracking table")

    def _run_pending_migrations(self, migration_dir: str):
        """Run pending migrations"""
        import glob

        # Get applied migrations
        applied_query = "SELECT version FROM schema_migrations ORDER BY applied_at"
        applied_results = DatabaseOperations.execute_query(applied_query, fetch="all")
        applied_versions = {row[0] for row in applied_results}

        # Find migration files
        migration_files = sorted(glob.glob(f"{migration_dir}/*.sql"))

        for migration_file in migration_files:
            # Extract version from filename (e.g., "001_initial_schema.sql")
            filename = os.path.basename(migration_file)
            version = filename.split('_')[0]

            if version not in applied_versions:
                logger.info(f"Applying migration: {filename}")
                self._apply_migration(migration_file, version, filename)

    def _apply_migration(self, migration_file: str, version: str, description: str):
        """Apply a single migration file"""
        try:
            with open(migration_file, 'r') as f:
                sql_content = f.read()

            # Split into individual statements and execute
            statements = self._split_sql_statements(sql_content)

            with DatabaseConfig.get_connection() as conn:
                with conn.cursor() as cur:
                    for statement in statements:
                        if statement.strip():
                            cur.execute(statement)

                    # Record migration
                    cur.execute(
                        "INSERT INTO schema_migrations (version, description) VALUES (%s, %s)",
                        (version, description)
                    )

            logger.info(f"Migration {version} applied successfully")

        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            raise

    def _split_sql_statements(self, sql_content: str) -> List[str]:
        """Split SQL content into individual statements"""
        import re

        # Remove comments and split on semicolons
        sql_content = re.sub(r'--.*$', '', sql_content, flags=re.MULTILINE)
        statements = []

        current_statement = ""
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_statement += line + " "
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""

        if current_statement.strip():
            statements.append(current_statement.strip())

        return statements

    def _create_prompt_templates_table(self):
        """Create prompt_templates table"""
        query = """
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT,
            category VARCHAR(100) NOT NULL,
            template_content TEXT NOT NULL,
            variables JSON,
            version VARCHAR(20) DEFAULT '1.0.0',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100)
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created prompt_templates table")

    def _create_prompt_usage_table(self):
        """Create prompt_usage table"""
        query = """
        CREATE TABLE IF NOT EXISTS prompt_usage (
            id VARCHAR(36) PRIMARY KEY,
            prompt_id VARCHAR(36) REFERENCES prompt_templates(id),
            ai_model VARCHAR(100),
            usage_count INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            avg_response_time INTEGER DEFAULT 0,
            last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created prompt_usage table")

    def _create_ai_configurations_table(self):
        """Create ai_configurations table"""
        query = """
        CREATE TABLE IF NOT EXISTS ai_configurations (
            id VARCHAR(36) PRIMARY KEY,
            model_name VARCHAR(255) UNIQUE NOT NULL,
            provider VARCHAR(100) NOT NULL,
            api_base_url VARCHAR(500),
            max_tokens INTEGER DEFAULT 4000,
            temperature DECIMAL(3,2) DEFAULT 0.7,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created ai_configurations table")

    def _create_generated_content_table(self):
        """Create generated_content table"""
        query = """
        CREATE TABLE IF NOT EXISTS generated_content (
            id VARCHAR(36) PRIMARY KEY,
            prompt_id VARCHAR(36) REFERENCES prompt_templates(id),
            ai_model VARCHAR(100),
            input_variables JSON,
            generated_content TEXT,
            tokens_used INTEGER,
            response_time INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created generated_content table")

    def _create_memory_entries_table(self):
        """Create memory_entries table"""
        query = """
        CREATE TABLE IF NOT EXISTS memory_entries (
            id VARCHAR(36) PRIMARY KEY,
            conversation_id VARCHAR(255) NOT NULL,
            session_id VARCHAR(255),
            role VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            entry_metadata JSON,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            ttl_seconds INTEGER DEFAULT 3600
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created memory_entries table")

    def _create_enhanced_memory_entries_table(self):
        """Create enhanced_memory_entries table"""
        query = """
        CREATE TABLE IF NOT EXISTS enhanced_memory_entries (
            id VARCHAR(36) PRIMARY KEY,
            conversation_id VARCHAR(255) NOT NULL,
            session_id VARCHAR(255),
            role VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            context_type VARCHAR(50) NOT NULL,
            importance_score DECIMAL(3,2) DEFAULT 0.5,
            tags JSON DEFAULT '[]',
            relationships JSON DEFAULT '[]',
            metadata JSON DEFAULT '{}',
            ttl_seconds INTEGER DEFAULT 3600,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created enhanced_memory_entries table")

    def _create_context_relationships_table(self):
        """Create context_relationships table"""
        query = """
        CREATE TABLE IF NOT EXISTS context_relationships (
            id VARCHAR(36) PRIMARY KEY,
            source_memory_id VARCHAR(36) NOT NULL,
            target_memory_id VARCHAR(36) NOT NULL,
            relationship_type VARCHAR(100) NOT NULL,
            strength DECIMAL(3,2) DEFAULT 1.0,
            metadata JSON DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_memory_id) REFERENCES enhanced_memory_entries(id),
            FOREIGN KEY (target_memory_id) REFERENCES enhanced_memory_entries(id)
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created context_relationships table")

    def _create_prompt_chains_table(self):
        """Create prompt_chains table"""
        query = """
        CREATE TABLE IF NOT EXISTS prompt_chains (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            steps JSON,
            inputs JSON,
            outputs JSON,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created prompt_chains table")

    def _create_prompt_chain_executions_table(self):
        """Create prompt_chain_executions table"""
        query = """
        CREATE TABLE IF NOT EXISTS prompt_chain_executions (
            id VARCHAR(36) PRIMARY KEY,
            chain_id VARCHAR(36) REFERENCES prompt_chains(id),
            execution_id VARCHAR(255),
            step_number INTEGER,
            prompt_id VARCHAR(36) REFERENCES prompt_templates(id),
            input_data JSON,
            output_data JSON,
            execution_time INTEGER,
            status VARCHAR(50) DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        DatabaseOperations.execute_query(query)
        logger.info("Created prompt_chain_executions table")


class PromptDataManager:
    """Main data manager for prompt engineering system using repository and service patterns"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.prompt_service = BusinessLogicPromptService()
        self.ai_service = AIService()

        # Initialize design pattern components
        self.prompt_service_facade = PromptService(
            template_manager=self,
            ai_service=self.ai_service,
            memory_manager=self
        )
        self.observer = PromptObserver()
        self.observer.attach(UsageTracker())
        self.observer.attach(CacheInvalidator())

        # Initialize database schema
        self._initialize_database()
        self._initialize_default_templates()

    def _initialize_database(self):
        """Initialize database schema and run migrations"""
        try:
            # Try to run migrations first
            self.db_manager.run_migrations()
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.warning(f"Migrations failed: {e}, falling back to table creation")
            # If migrations fail, create tables directly
            self.db_manager.create_tables()

    def _initialize_default_templates(self):
        """Initialize default prompt templates if none exist"""
        templates = self.prompt_service.list_templates()

        if not templates:
            self._create_default_templates()

    def _create_default_templates(self):
        """Create default prompt templates for common use cases"""

        default_templates = [
            {
                "name": "business_logic_implementation",
                "description": "Standard template for implementing business logic",
                "category": "development",
                "template_content": """
You are an expert software developer implementing business logic for {{business_domain}}.

Requirements:
{{requirements}}

Constraints:
{{constraints}}

Please provide the implementation following these guidelines:
1. Use clean, maintainable code
2. Include proper error handling
3. Add comprehensive documentation
4. Follow best practices for {{business_domain}}

Output the code in the following format:
{{output_format}}
""",
                "variables": ["business_domain", "requirements", "constraints", "output_format"]
            },
            {
                "name": "api_design",
                "description": "Standard template for REST API design",
                "category": "architecture",
                "template_content": """
Design a REST API for {{resource_name}} with the following requirements:

Operations needed: {{operations}}
Data structure: {{data_structure}}
Authentication: {{authentication}}

Please provide:
1. API endpoint specifications
2. Request/Response examples
3. Data models
4. Error handling strategy
5. Security considerations

Format the response as a comprehensive API design document.
""",
                "variables": ["resource_name", "operations", "data_structure", "authentication"]
            },
            {
                "name": "database_schema_design",
                "description": "Standard template for database schema design",
                "category": "data",
                "template_content": """
Design a database schema for {{entity_name}} with the following requirements:

Relationships: {{relationships}}
Constraints: {{constraints}}
Performance requirements: {{indexes}}

Please provide:
1. Table/entity definitions
2. Field specifications with types and constraints
3. Relationship mappings
4. Index recommendations
5. Migration strategy

Format as a database design document with SQL examples.
""",
                "variables": ["entity_name", "relationships", "constraints", "indexes"]
            },
            {
                "name": "advanced_reasoning_chain",
                "description": "Advanced multi-step reasoning with context integration",
                "category": "techniques",
                "template_content": """
You are an advanced AI reasoning system. Analyze the following problem using sophisticated multi-step reasoning:

PROBLEM: {{problem_statement}}

{{#if context_data}}
RELEVANT CONTEXT:
{{context_data}}
{{/if}}

{{#if constraints}}
CONSTRAINTS:
{{#each constraints}}
- {{this}}
{{/each}}
{{/if}}

REASONING APPROACH:
1. **Problem Decomposition**: Break down the problem into core components and sub-problems
2. **Context Analysis**: Analyze how existing context relates to the current problem
3. **Alternative Perspectives**: Consider multiple viewpoints and approaches
4. **Solution Synthesis**: Develop comprehensive solution strategies
5. **Risk Assessment**: Identify potential issues and mitigation strategies
6. **Implementation Planning**: Create detailed execution steps

{{#if evaluation_criteria}}
EVALUATION CRITERIA:
{{#each evaluation_criteria}}
- {{this}}
{{/each}}
{{/if}}

REQUIREMENTS:
- Use step-by-step reasoning throughout
- Consider edge cases and error conditions
- Provide implementation-ready solutions
- Include testing strategies and validation approaches

OUTPUT FORMAT:
Provide your analysis in the following structured format:

## STEP 1: Problem Decomposition
[Break down the problem into core components]

## STEP 2: Context Integration
[Analyze how existing context applies to this problem]

## STEP 3: Multi-Perspective Analysis
[Consider different approaches and viewpoints]

## STEP 4: Solution Architecture
[Design the overall solution structure]

## STEP 5: Detailed Implementation
[Provide specific implementation steps and code examples]

## STEP 6: Risk Assessment & Testing
[Identify risks and provide comprehensive testing strategy]

## FINAL RECOMMENDATION
[Provide your final recommendation with justification]
""",
                "variables": ["problem_statement", "context_data", "constraints", "evaluation_criteria"]
            },
            {
                "name": "code_architecture_design",
                "description": "Advanced code architecture and design patterns",
                "category": "architecture",
                "template_content": """
Design a comprehensive software architecture for the following requirements:

REQUIREMENTS: {{requirements}}

{{#if existing_codebase}}
EXISTING CODEBASE ANALYSIS:
{{existing_codebase}}
{{/if}}

{{#if constraints}}
ARCHITECTURAL CONSTRAINTS:
{{#each constraints}}
- {{this}}
{{/each}}
{{/if}}

{{#if performance_requirements}}
PERFORMANCE REQUIREMENTS:
{{performance_requirements}}
{{/if}}

DESIGN PRINCIPLES TO FOLLOW:
- SOLID Principles (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- Clean Architecture patterns
- Domain-Driven Design principles
- Microservices or Monolith decision rationale
- Scalability and maintainability focus

REQUIRED ANALYSIS SECTIONS:

## 1. SYSTEM OVERVIEW
- High-level architecture description
- Technology stack recommendations
- Deployment strategy overview

## 2. COMPONENT ARCHITECTURE
- Core components identification
- Component responsibilities
- Inter-component communication patterns

## 3. DATA ARCHITECTURE
- Data models and relationships
- Storage strategy (Database, Cache, File System)
- Data flow diagrams

## 4. APPLICATION LAYER ARCHITECTURE
- Presentation layer design
- Application service layer
- Domain layer structure
- Infrastructure layer implementation

## 5. CROSS-CUTTING CONCERNS
- Security architecture
- Logging and monitoring strategy
- Error handling patterns
- Configuration management

## 6. DESIGN PATTERNS APPLICATION
- Creational patterns (Factory, Builder, Singleton, etc.)
- Structural patterns (Adapter, Decorator, Facade, etc.)
- Behavioral patterns (Observer, Strategy, Command, etc.)

## 7. SCALABILITY CONSIDERATIONS
- Horizontal vs Vertical scaling strategy
- Load balancing approach
- Caching strategies
- Performance optimization patterns

## 8. CODE ORGANIZATION
- Package/module structure
- Naming conventions
- Code documentation standards
- Testing strategy

## 9. DEPLOYMENT ARCHITECTURE
- Development environment setup
- Staging environment configuration
- Production deployment strategy
- CI/CD pipeline design

## 10. MAINTENANCE & EVOLUTION
- Code refactoring strategies
- Version management approach
- Dependency management
- Technical debt management

Provide detailed explanations for each section with code examples where applicable.
""",
                "variables": ["requirements", "existing_codebase", "constraints", "performance_requirements"]
            },
            {
                "name": "advanced_data_analysis",
                "description": "Sophisticated data analysis and insights generation",
                "category": "data",
                "template_content": """
Perform advanced data analysis on the following dataset:

DATASET: {{dataset_description}}

{{#if data_schema}}
DATA SCHEMA:
{{data_schema}}
{{/if}}

ANALYSIS OBJECTIVES:
{{#each analysis_objectives}}
- {{this}}
{{/each}}

{{#if analysis_type}}
ANALYSIS TYPE: {{analysis_type}}
{{/if}}

ANALYTICAL APPROACH:

## 1. DATA EXPLORATION & PROFILING
- Data quality assessment
- Missing values analysis
- Outlier detection
- Distribution analysis
- Correlation studies

## 2. STATISTICAL ANALYSIS
- Descriptive statistics
- Inferential statistics
- Hypothesis testing
- Confidence intervals
- Statistical significance

## 3. PATTERN RECOGNITION
- Trend analysis
- Seasonality detection
- Anomaly detection
- Clustering analysis
- Classification patterns

## 4. PREDICTIVE MODELING
- Regression analysis
- Time series forecasting
- Machine learning models
- Model validation
- Prediction accuracy

## 5. DATA VISUALIZATION STRATEGY
- Chart type recommendations
- Dashboard design
- Interactive visualizations
- Storytelling with data

## 6. BUSINESS INSIGHTS
- Key findings summary
- Business implications
- Actionable recommendations
- Risk assessment
- Opportunity identification

TECHNICAL REQUIREMENTS:
- Use appropriate statistical methods
- Apply data preprocessing techniques
- Implement feature engineering if needed
- Consider computational complexity
- Ensure reproducibility

{{#if output_format}}
OUTPUT FORMAT: {{output_format}}
{{/if}}

Provide comprehensive analysis with code examples, mathematical formulations, and practical recommendations.
""",
                "variables": ["dataset_description", "data_schema", "analysis_objectives", "analysis_type", "output_format"]
            },
            {
                "name": "comprehensive_testing_strategy",
                "description": "Advanced testing strategy with multiple testing types",
                "category": "quality",
                "template_content": """
Develop a comprehensive testing strategy for the following system:

SYSTEM DESCRIPTION: {{system_description}}

{{#if architecture_type}}
ARCHITECTURE TYPE: {{architecture_type}}
{{/if}}

{{#if technology_stack}}
TECHNOLOGY STACK: {{technology_stack}}
{{/if}}

TESTING STRATEGY FRAMEWORK:

## 1. TEST PLANNING & STRATEGY
- Testing objectives and scope
- Testing levels definition (Unit, Integration, System, E2E)
- Test environment strategy
- Test data management approach
- Risk-based testing prioritization

## 2. UNIT TESTING
- Component isolation strategies
- Mocking and stubbing approaches
- Test coverage targets
- Mutation testing considerations
- Performance unit tests

## 3. INTEGRATION TESTING
- Component integration patterns
- API contract testing
- Database integration testing
- Third-party service integration
- Message queue testing

## 4. SYSTEM TESTING
- End-to-end user journey testing
- Business process validation
- System performance testing
- Security testing approach
- Compatibility testing

## 5. PERFORMANCE TESTING
- Load testing scenarios
- Stress testing limits
- Volume testing with large datasets
- Scalability testing
- Resource utilization analysis

## 6. SECURITY TESTING
- Authentication and authorization testing
- Input validation testing
- SQL injection prevention
- XSS protection validation
- Security headers verification

## 7. AUTOMATION STRATEGY
- Test automation framework selection
- CI/CD integration
- Automated test execution
- Test result reporting
- Flaky test management

## 8. QUALITY GATES
- Code coverage thresholds
- Performance benchmarks
- Security vulnerability scans
- Code quality metrics
- Automated deployment gates

## 9. MONITORING & OBSERVABILITY
- Test metrics collection
- Performance monitoring
- Error tracking and alerting
- Log analysis strategy
- Test environment monitoring

## 10. MAINTENANCE & EVOLUTION
- Test maintenance strategies
- Test debt management
- Test refactoring approaches
- Knowledge sharing and documentation
- Continuous improvement process

IMPLEMENTATION ROADMAP:
- Phase 1: Core testing infrastructure
- Phase 2: Unit and integration testing
- Phase 3: System and E2E testing
- Phase 4: Performance and security testing
- Phase 5: Optimization and maintenance

{{#if compliance_requirements}}
COMPLIANCE REQUIREMENTS:
{{compliance_requirements}}
{{/if}}

Provide detailed implementation guidance with code examples and best practices.
""",
                "variables": ["system_description", "architecture_type", "technology_stack", "compliance_requirements"]
            },
            {
                "name": "technical_documentation",
                "description": "Comprehensive technical documentation generation",
                "category": "communication",
                "template_content": """
Generate comprehensive technical documentation for the following component:

COMPONENT: {{component_name}}

{{#if component_type}}
COMPONENT TYPE: {{component_type}}
{{/if}}

{{#if implementation_language}}
IMPLEMENTATION LANGUAGE: {{implementation_language}}
{{/if}}

DOCUMENTATION REQUIREMENTS:

## 1. OVERVIEW & PURPOSE
- Component description and purpose
- Business value and use cases
- Target audience identification
- Key features and capabilities

## 2. ARCHITECTURE & DESIGN
- High-level architecture overview
- Component relationships and dependencies
- Design patterns and principles used
- Technology stack and frameworks

## 3. API REFERENCE
- Public interface documentation
- Method signatures and parameters
- Return types and error conditions
- Usage examples and code samples

## 4. CONFIGURATION & SETUP
- Installation and setup instructions
- Configuration options and parameters
- Environment requirements
- Dependency management

## 5. USAGE GUIDE
- Basic usage examples
- Advanced usage patterns
- Best practices and recommendations
- Common pitfalls and solutions

## 6. INTEGRATION PATTERNS
- Integration with other components
- Event-driven interactions
- Data flow and transformation
- Error handling strategies

## 7. PERFORMANCE CHARACTERISTICS
- Performance benchmarks and metrics
- Scalability considerations
- Resource utilization patterns
- Optimization recommendations

## 8. SECURITY CONSIDERATIONS
- Security features and mechanisms
- Authentication and authorization
- Data protection and privacy
- Security best practices

## 9. TESTING STRATEGY
- Unit testing approach
- Integration testing patterns
- Performance testing scenarios
- Security testing considerations

## 10. TROUBLESHOOTING
- Common issues and solutions
- Debugging techniques and tools
- Error messages and interpretations
- Support and maintenance procedures

## 11. DEVELOPMENT GUIDE
- Development environment setup
- Code contribution guidelines
- Testing and validation procedures
- Release and deployment process

## 12. CHANGELOG & VERSION HISTORY
- Version compatibility information
- Migration guides for breaking changes
- Deprecated features and alternatives
- Future roadmap and enhancements

{{#if include_examples}}
Include practical examples and code snippets throughout the documentation.
{{/if}}

{{#if audience_type}}
AUDIENCE: {{audience_type}}
{{/if}}

{{#if documentation_format}}
FORMAT: {{documentation_format}}
{{/if}}

Provide comprehensive documentation with clear structure, practical examples, and actionable guidance.
""",
                "variables": ["component_name", "component_type", "implementation_language", "include_examples", "audience_type", "documentation_format"]
            },
            {
                "name": "meta_prompt_optimization",
                "description": "Meta-prompting for generating optimized prompts",
                "category": "techniques",
                "template_content": """
You are a meta-prompting expert. Your task is to create an optimized prompt for the following use case:

TARGET TASK: {{target_task}}

{{#if task_description}}
DETAILED DESCRIPTION: {{task_description}}
{{/if}}

{{#if context_information}}
RELEVANT CONTEXT: {{context_information}}
{{/if}}

META-PROMPTING OBJECTIVES:
1. **Clarity**: Ensure the generated prompt is crystal clear and unambiguous
2. **Effectiveness**: Maximize the quality and relevance of AI responses
3. **Efficiency**: Minimize token usage while maintaining effectiveness
4. **Robustness**: Handle edge cases and variations in input
5. **Adaptability**: Work across different AI models and capabilities

PROMPT ENGINEERING PRINCIPLES TO APPLY:

## 1. STRUCTURAL OPTIMIZATION
- Clear task definition and boundaries
- Explicit input/output specifications
- Structured response format requirements
- Error handling and edge case management

## 2. CONTEXTUAL ENHANCEMENT
- Relevant background information inclusion
- Domain-specific terminology and concepts
- Constraint and limitation specifications
- Success criteria and evaluation metrics

## 3. INSTRUCTIONAL DESIGN
- Step-by-step reasoning guidance
- Example-based learning when beneficial
- Iterative refinement instructions
- Quality assurance checkpoints

## 4. PSYCHOLOGICAL FACTORS
- Role assignment and persona activation
- Motivation and goal orientation
- Confidence building and encouragement
- Feedback loops and improvement mechanisms

## 5. TECHNICAL CONSIDERATIONS
- Model capability awareness
- Token efficiency optimization
- Output format standardization
- Error prevention and recovery

GENERATE AN OPTIMIZED PROMPT THAT:

1. **Clearly defines the task** with specific objectives and deliverables
2. **Provides sufficient context** without overwhelming the model
3. **Specifies exact input/output formats** with examples when helpful
4. **Includes quality control measures** and validation criteria
5. **Guides reasoning process** with structured thinking frameworks
6. **Handles variations and edge cases** proactively
7. **Maximizes effectiveness** while minimizing unnecessary verbosity

{{#if target_audience}}
TARGET AUDIENCE: {{target_audience}}
{{/if}}

{{#if complexity_level}}
COMPLEXITY LEVEL: {{complexity_level}}
{{/if}}

{{#if response_format}}
RESPONSE FORMAT: {{response_format}}
{{/if}}

Provide the optimized prompt along with a detailed rationale for your design choices.
""",
                "variables": ["target_task", "task_description", "context_information", "target_audience", "complexity_level", "response_format"]
            }
        ]

        for template_data in default_templates:
            try:
                self.prompt_service.create_template(template_data)
            except Exception as e:
                logger.error(f"Failed to create default template {template_data['name']}: {e}")

    # Delegate methods to the prompt service
    def build_enhanced_prompt(self, template_name: str, context: str, variables: Dict[str, Any], instructions: List[str] = None) -> str:
        """Build an enhanced prompt using the Builder pattern"""
        builder = PromptBuilder()
        builder.add_section("Context", context)

        for name, value in variables.items():
            builder.add_variable(name, value)

        if instructions:
            for instruction in instructions:
                builder.add_instruction(instruction)

        return builder.build()

    def render_prompt_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render a prompt template with variables"""
        return self.prompt_service.render_template(template_name, variables)

    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """List all active prompt templates"""
        return self.prompt_service.list_templates(category)

    def get_available_categories(self) -> List[str]:
        """Get all available prompt categories"""
        return self.prompt_service.get_categories()

    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """Get all templates in a specific category"""
        return self.prompt_service.get_templates_by_category(category)

    def record_prompt_usage(self, prompt_id, ai_model: str, response_time: int, success: bool = True):
        """Record prompt usage statistics"""
        return self.prompt_service.record_usage(prompt_id, ai_model, response_time, success)

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        return self.prompt_service.get_usage_statistics()

    def store_memory_entry(self, conversation_id: str, session_id: str, role: str, content: str, entry_metadata: Optional[Dict[str, Any]] = None, ttl_seconds: int = 3600) -> str:
        """Store a memory entry for conversation history"""
        return self.prompt_service.store_memory_entry(conversation_id, session_id, role, content, entry_metadata, ttl_seconds)

    def retrieve_memory_entries(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve memory entries for a conversation"""
        return self.prompt_service.retrieve_memory_entries(conversation_id, limit)

    def clear_memory_entries(self, conversation_id: str) -> int:
        """Clear all memory entries for a conversation"""
        return self.prompt_service.clear_memory_entries(conversation_id)

    def store_enhanced_memory_entry(
        self,
        conversation_id: str,
        session_id: str,
        role: str,
        content: str,
        context_type: str,
        importance_score: float = 0.5,
        tags: List[str] = None,
        relationships: List[str] = None,
        metadata: Dict[str, Any] = None,
        ttl_seconds: int = 3600
    ) -> str:
        """Store an enhanced memory entry with sophisticated context management"""
        return self.prompt_service.store_enhanced_memory_entry(
            conversation_id, session_id, role, content, context_type,
            importance_score, tags, relationships, metadata, ttl_seconds
        )

    def retrieve_enhanced_memory_entries(
        self,
        conversation_id: str,
        context_type: str = None,
        tags: List[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve enhanced memory entries with advanced filtering"""
        return self.prompt_service.retrieve_enhanced_memory_entries(
            conversation_id, context_type, tags, limit
        )

    def get_related_memories(self, memory_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories related to a specific memory entry"""
        return self.prompt_service.get_related_memories(memory_id, limit)

    def create_context_relationship(
        self,
        source_memory_id: str,
        target_memory_id: str,
        relationship_type: str,
        strength: float = 1.0,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a context relationship between memory entries"""
        return self.prompt_service.create_context_relationship(
            source_memory_id, target_memory_id, relationship_type, strength, metadata
        )

    def get_context_relationships(self, memory_id: str) -> List[Dict[str, Any]]:
        """Get all context relationships for a memory entry"""
        return self.prompt_service.get_context_relationships(memory_id)

    def clear_enhanced_memory_entries(self, conversation_id: str) -> int:
        """Clear all enhanced memory entries for a conversation"""
        return self.prompt_service.clear_enhanced_memory_entries(conversation_id)

    def build_memory_context(
        self,
        conversation_id: str,
        context_types: List[str] = None,
        max_entries: int = 20,
        min_importance: float = 0.0
    ) -> str:
        """Build a comprehensive memory context for AI processing"""
        return self.prompt_service.build_memory_context(
            conversation_id, context_types, max_entries, min_importance
        )

    def get_available_techniques(self) -> List[str]:
        """Get all available prompt engineering techniques"""
        techniques = [
            "zero_shot", "few_shot", "chain_of_thought", "tree_of_thoughts",
            "react", "self_consistency", "meta_prompting", "prompt_chaining"
        ]
        return techniques

    def render_technique_template(self, technique: str, variables: Dict[str, Any]) -> str:
        """Render a specific prompt engineering technique template"""
        technique_templates = {
            "zero_shot": """
Direct approach for {{task_description}}.

Context: {{context}}

Expected output format: {{expected_output}}

Please provide a direct response without additional examples.
""",
            "few_shot": """
Task: {{task_description}}

Examples:
{{examples}}

Now solve this: {{input_format}}

Output format: {{output_format}}
""",
            "chain_of_thought": """
Problem: {{problem_statement}}

Please solve this step by step:

1. {{reasoning_steps}}

Final answer format: {{final_answer_format}}
""",
            "tree_of_thoughts": """
Problem: {{problem}}

Possible reasoning paths:
{{possible_paths}}

Evaluation criteria: {{evaluation_criteria}}

Please explore multiple reasoning paths and select the best approach.
""",
            "react": """
Task: {{task}}

Available actions: {{available_actions}}

Reasoning guidance: {{reasoning_guidance}}

Please reason step by step and take appropriate actions.
""",
            "self_consistency": """
Task: {{task}}

Reasoning prompts to consider:
{{reasoning_prompts}}

Consistency check: {{consistency_check}}

Please provide multiple reasoning approaches and verify consistency.
""",
            "meta_prompting": """
I need to create a prompt for: {{task_description}}

Requirements for the prompt:
{{prompt_requirements}}

Optimization criteria: {{optimization_criteria}}

Please generate an optimized prompt that meets these requirements.
""",
            "prompt_chaining": """
Initial input: {{initial_input}}

Chain of steps:
{{chain_steps}}

Output processing: {{output_processing}}

Please execute this prompt chain step by step.
"""
        }

        if technique not in technique_templates:
            raise ValueError(f"Unknown technique: {technique}")

        template_content = technique_templates[technique]

        # Replace variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            template_content = template_content.replace(placeholder, str(var_value))

        return template_content

    def get_ai_configurations(self) -> List[Dict[str, Any]]:
        """Get all AI model configurations"""
        return [config.dict() for config in self.ai_service.list_configurations()]

    def create_ai_configuration(self, model_name: str, provider: str, api_base_url: str = None, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """Create a new AI configuration"""
        config = self.ai_service.create_configuration({
            "model_name": model_name,
            "provider": provider,
            "api_base_url": api_base_url,
            "max_tokens": max_tokens,
            "temperature": temperature
        })
        return str(config.id)

    def store_generated_content(self, prompt_id, ai_model: str, input_variables: Dict[str, Any], generated_content: str, tokens_used: int, response_time: int) -> str:
        """Store generated content"""
        return self.prompt_service.store_generated_content(prompt_id, ai_model, input_variables, generated_content, tokens_used, response_time)

    def get_generated_content(self, prompt_id, limit: int = 10) -> List[Dict[str, Any]]:
        """Get generated content for a prompt"""
        return self.prompt_service.get_generated_content(prompt_id, limit)


# Global instance for backward compatibility
_data_manager = None

def get_data_manager():
    """Get global data manager instance"""
    global _data_manager
    if _data_manager is None:
        _data_manager = PromptDataManager()
    return _data_manager
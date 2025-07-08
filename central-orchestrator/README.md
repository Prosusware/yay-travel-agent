# LangGraph Phone Call & Research Agent

A sophisticated LangGraph-based agent system that can perform research tasks and make phone calls using ElevenLabs voice synthesis via Twilio API. The agent maintains state, tracks task completion, and manages key facts throughout the execution process.

## Features

### Core Capabilities
- **Gemini AI Integration**: Uses Google's Gemini for intelligent inference, planning, and decision-making throughout the workflow
- **Phone Call Integration**: Make automated phone calls using ElevenLabs voice and Twilio API with AI-generated scripts
- **Research Capabilities**: Search the web using Tavily API with AI-optimized queries and intelligent result analysis
- **State Management**: Track task progress, key facts, and completion status with AI-powered analysis
- **Task Completion Checking**: Automatically assess if tasks are complete after each step using intelligent scoring
- **Requirement Tracking**: Monitor what's missing and what's been accomplished with AI-powered requirement detection

### Two Agent Types

#### 1. Basic Agent (`agent.py`)
- Gemini-powered planning, analysis, and routing decisions
- AI-generated search queries and call scripts
- Intelligent task completion analysis
- Essential phone calling and research capabilities

#### 2. Advanced Agent (`advanced_agent.py`)
- Full Gemini integration for all inference tasks
- AI-powered requirement detection and completion scoring
- Enhanced state management with intelligent analysis
- Context memory with AI-driven continuity
- Execution logging and step-by-step analysis
- Priority-based task routing with AI optimization

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
Copy `config.env.example` to `.env` and fill in your API keys:

```bash
# Tavily API Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# ElevenLabs API Configuration
ELEVENLABS_API_KEY=sk_335b9a30cac6c93af60fcc59af3f84a0f787429ba5df4e63
ELEVENLABS_AGENT_ID=agent_01jy7m698wev1sw2jpkk6gkh3m
ELEVENLABS_PHONE_NUMBER_ID=phnum_01jy7qdrfgf2atee6dg099s47x

# Phone Configuration
TARGET_PHONE_NUMBER=447874943523
```

## API Requirements

### Required Services
1. **Mistral API**: For AI inference and decision-making
   - Sign up at [Mistral AI](https://mistral.ai)
   - Get your API key
   - Supports models like `mistral-large-latest`, `mistral-medium`, etc.

2. **Tavily API**: For web search capabilities
   - Sign up at [Tavily](https://tavily.com)
   - Get your API key
   
3. **ElevenLabs ConvAI**: For outbound phone calls
   - Sign up at [ElevenLabs](https://elevenlabs.io)
   - Create a ConvAI agent and get your agent ID
   - Get your phone number ID for outbound calls
   - Get your API key for authentication

### ElevenLabs API Call Format
The agents use the ElevenLabs ConvAI API with this payload structure:
```json
{
  "agent_id": "agent_01jy7m698wev1sw2jpkk6gkh3m",
  "agent_phone_number_id": "phnum_01jy7qdrfgf2atee6dg099s47x",
  "to_number": "447874943523"
}
```

Headers required:
```
Xi-Api-Key: sk_335b9a30cac6c93af60fcc59af3f84a0f787429ba5df4e63
Api-Key: xi-api-key
Content-Type: application/json
```

## Usage

### Quick Start
```python
from agent import run_agent
from advanced_agent import run_enhanced_agent

# Basic agent
result = run_agent(
    task="Call the client to confirm meeting tomorrow",
    phone_number="447874943523"
)

# Advanced agent
result = run_enhanced_agent(
    task="Research AI trends and call client to discuss",
    phone_number="447874943523",
    max_steps=10
)
```

### Running Examples
```bash
python example_usage.py
```

### Command Line Usage
```bash
# Basic agent
python agent.py

# Advanced agent  
python advanced_agent.py
```

## Agent State Management

### Basic Agent State
```python
{
    "messages": [],                    # Conversation history
    "current_task": "",                # Current task description
    "task_complete": false,            # Completion status
    "completion_status": "",           # Status message
    "missing_requirements": [],        # What's still needed
    "key_facts": {},                   # Important information collected
    "tavily_results": [],              # Research results
    "phone_call_results": [],          # Call outcomes
    "step_count": 0                    # Number of steps executed
}
```

### Advanced Agent State
```python
{
    "messages": [],                    # Conversation history
    "current_task": "",                # Current task description
    "task_status": "pending",          # pending|in_progress|completed|failed
    "task_requirements": [],           # Detailed requirement tracking
    "completion_score": 0.0,           # Score from 0.0 to 1.0
    "key_facts": {},                   # Enhanced fact storage
    "tavily_results": [],              # Research results with metadata
    "phone_call_results": [],          # Detailed call results
    "step_count": 0,                   # Current step number
    "max_steps": 15,                   # Maximum allowed steps
    "execution_log": [],               # Step-by-step execution log
    "context_memory": {}               # Context for continuity
}
```

## Task Requirements Detection

The agents automatically detect task requirements based on keywords:

- **Phone Call**: "call", "phone", "contact", "speak"
- **Research**: "research", "find", "search", "information", "details"
- **Confirmation**: "confirm", "verify", "check", "validate"
- **Follow-up**: "follow up", "schedule", "arrange", "plan"

## Workflow

1. **AI Planning Phase**: Mistral analyzes task and intelligently determines requirements
2. **AI Research Phase**: Mistral generates optimal search queries and analyzes results using Tavily API (if needed)
3. **AI Phone Call Phase**: Mistral creates personalized call scripts and executes calls via ElevenLabs/Twilio (if needed)
4. **AI Completion Check**: Mistral assesses task completion with intelligent scoring
5. **AI Routing**: Mistral determines the next best action
6. **Repeat**: Continue until task is complete or max steps reached

## Error Handling

- **API Failures**: Graceful handling of service unavailability
- **Invalid Phone Numbers**: Validation and error reporting
- **Missing Environment Variables**: Clear error messages
- **Timeout Protection**: Prevents infinite loops with max step limits

## Customization

### Adding New Requirements
```python
def analyze_task_requirements(task: str) -> List[TaskRequirement]:
    requirements = []
    
    # Add your custom requirement detection
    if "email" in task.lower():
        requirements.append(TaskRequirement(
            name="email_send",
            description="Send an email"
        ))
    
    return requirements
```

### Custom Completion Logic
```python
def calculate_completion_score(state: AdvancedAgentState) -> float:
    # Implement your custom scoring logic
    # Return value between 0.0 and 1.0
    pass
```

## Example Tasks

### Simple Tasks
- "Call +1234567890 to confirm appointment"
- "Research latest AI developments"
- "Find information about company X"

### Complex Tasks
- "Research market trends in AI and call the client to discuss implementation"
- "Find contact information for company Y and call to schedule a meeting"
- "Research competitor analysis and call team lead to review findings"

## Troubleshooting

### Common Issues

1. **Environment Variables Not Set**
   - Check your `.env` file
   - Ensure all required variables are present

2. **Mistral API Errors**
   - Verify your Mistral API key is correct
   - Check your account quota and model access
   - Ensure the model name is valid (e.g., `mistral-large-latest`)

3. **Tavily API Errors**
   - Verify your API key is correct
   - Check your account quota

4. **ElevenLabs Phone Call Failures**
   - Verify your ElevenLabs API key is correct
   - Check phone number format (international format without +, e.g., 447874943523)
   - Ensure your agent ID and phone number ID are valid
   - Check your ElevenLabs account has sufficient credits

5. **Import Errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version compatibility
   - Ensure `langchain-mistralai` is properly installed

### Debug Mode
Set environment variable for verbose logging:
```bash
export DEBUG=1
python agent.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check the LICENSE file for details.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the example usage
3. Create an issue with detailed information about your problem 
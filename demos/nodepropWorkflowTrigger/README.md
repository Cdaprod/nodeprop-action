Here’s the structure written as skeleton code-like lists, defining the events that each layer publishes and receives:

1. Actor Layer

// Publishes
- RegisterRepository(repoName string, actions []string, workflows []string)
- TriggerAllFlows(repoName string, token string)
- TriggerCustomFlow(repoName string, flowType string, flowName string, token string, params map[string]string)

// Receives
- RepoRegisteredEvent(repoName string, status string) // From Facade Layer
- FlowsTriggeredEvent(repoName string, status string) // From Facade Layer
- CustomFlowTriggeredEvent(repoName string, flowName string, status string) // From Facade Layer
- ErrorEvent(repoName string, error string) // From Facade Layer

2. Facade Layer

// Publishes
- RegisterRepoInRegistry(repoName string, actions []string, workflows []string)
- ExecuteRepoFlows(repoName string, token string)
- ExecuteSpecificFlow(repoName string, flowType string, flowName string, token string, params map[string]string)

// Receives
- RepoRegistrationResult(repoName string, status string) // From Repository Layer
- WorkflowExecutionResult(repoName string, flowName string, status string) // From Flow Layer
- ActionExecutionResult(repoName string, actionName string, status string) // From Flow Layer
- ErrorEvent(sourceLayer string, error string) // From Repository or Flow Layer

3. Flow Layer

// Publishes
- ExecuteWorkflow(repoName string, workflowName string, params map[string]string)
- ExecuteAction(repoName string, actionName string, params map[string]string)
- WorkflowExecutionStatus(repoName string, workflowName string, status string)
- ActionExecutionStatus(repoName string, actionName string, status string)

// Receives
- WorkflowTriggerRequest(repoName string, workflowName string, params map[string]string) // From Facade Layer
- ActionTriggerRequest(repoName string, actionName string, params map[string]string) // From Facade Layer
- RepoMetadataUpdate(repoName string, metadata map[string]interface{}) // From Repository Layer

4. Repository Layer

// Publishes
- RepoStateUpdated(repoName string, state map[string]interface{})
- RepoWorkflowList(repoName string, workflows []string)
- RepoActionList(repoName string, actions []string)
- RepoMetadata(repoName string, metadata map[string]interface{})

// Receives
- RegisterRepoRequest(repoName string, actions []string, workflows []string) // From Facade Layer
- UpdateRepoState(repoName string, state map[string]interface{}) // From Flow Layer
- FetchRepoWorkflows(repoName string) // From Facade Layer
- FetchRepoActions(repoName string) // From Facade Layer
- FetchRepoMetadata(repoName string) // From Flow Layer

5. Integration Layer

// Publishes
- GitHubWorkflowTriggered(repoName string, workflowName string, status string)
- GitHubActionTriggered(repoName string, actionName string, status string)
- ExternalMetadataFetched(repoName string, metadata map[string]interface{})

// Receives
- TriggerGitHubWorkflowRequest(repoName string, workflowName string, params map[string]string) // From Flow Layer
- TriggerGitHubActionRequest(repoName string, actionName string, params map[string]string) // From Flow Layer
- FetchExternalMetadataRequest(repoName string, source string) // From Repository Layer

Relationships Between Layers

Actor -> Facade

actor.RegisterRepository(repoName, actions, workflows) -> facade.RegisterRepoInRegistry(repoName, actions, workflows)
actor.TriggerAllFlows(repoName, token) -> facade.ExecuteRepoFlows(repoName, token)
actor.TriggerCustomFlow(repoName, "workflow", workflowName, token, params) -> facade.ExecuteSpecificFlow(repoName, "workflow", workflowName, token, params)

Facade -> Repository

facade.RegisterRepoInRegistry(repoName, actions, workflows) -> repository.RegisterRepoRequest(repoName, actions, workflows)
facade.ExecuteRepoFlows(repoName, token) -> repository.FetchRepoWorkflows(repoName)

Facade -> Flow

facade.ExecuteRepoFlows(repoName, token) -> flow.ExecuteWorkflow(repoName, workflowName, params)
facade.ExecuteSpecificFlow(repoName, "action", actionName, token, params) -> flow.ExecuteAction(repoName, actionName, params)

Flow -> Integration

flow.ExecuteWorkflow(repoName, workflowName, params) -> integration.TriggerGitHubWorkflowRequest(repoName, workflowName, params)
flow.ExecuteAction(repoName, actionName, params) -> integration.TriggerGitHubActionRequest(repoName, actionName, params)

Repository -> Facade

repository.RepoStateUpdated(repoName, state) -> facade.RepoRegistrationResult(repoName, status)
repository.RepoWorkflowList(repoName, workflows) -> facade.WorkflowExecutionResult(repoName, workflowName, status)
repository.RepoActionList(repoName, actions) -> facade.ActionExecutionResult(repoName, actionName, status)

This skeleton defines the roles and responsibilities at each layer and how they interact by publishing and receiving events. It ensures modularity and clarity, enabling scalability as you extend functionality in your system.
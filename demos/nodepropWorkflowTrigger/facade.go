package flow

// FlowFacade defines the facade interface.
type FlowFacade interface {
	RegisterRepo(repo string, actions []string, workflows []string) error
	TriggerRepoFlows(repo string, token string) error
	TriggerCustomFlow(repo string, flowType string, name string, token string, params map[string]string) error
}

type flowFacadeImpl struct {
	triggerManager *flow.TriggerManager
	repoRegistry   *flow.RepositoryRegistry
}

// NewFlowFacade creates a new FlowFacade.
func NewFlowFacade(triggerManager *flow.TriggerManager, repoRegistry *flow.RepositoryRegistry) FlowFacade {
	return &flowFacadeImpl{triggerManager: triggerManager, repoRegistry: repoRegistry}
}

func (f *flowFacadeImpl) RegisterRepo(repo string, actions []string, workflows []string) error {
	f.repoRegistry.RegisterRepo(repo, actions, workflows)
	return nil
}

func (f *flowFacadeImpl) TriggerRepoFlows(repo string, token string) error {
	return f.repoRegistry.TriggerForRepo(repo, f.triggerManager, token)
}

func (f *flowFacadeImpl) TriggerCustomFlow(repo string, flowType string, name string, token string, params map[string]string) error {
	switch flowType {
	case "action":
		return f.triggerManager.ExecuteAction(name, repo, token, params)
	case "workflow":
		return f.triggerManager.ExecuteWorkflow(name, repo, token, params)
	default:
		return fmt.Errorf("invalid flow type: %s", flowType)
	}
}
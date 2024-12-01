package flow

type Actor interface {
	RegisterRepo(repo string, actions []string, workflows []string) error
	RunRepoFlows(repo string, token string) error
	RunCustomFlow(repo string, flowType string, name string, token string, params map[string]string) error
}

type actorImpl struct {
	flowFacade facade.FlowFacade
}

// NewActor creates a new Actor instance.
func NewActor(flowFacade facade.FlowFacade) Actor {
	return &actorImpl{flowFacade: flowFacade}
}

func (a *actorImpl) RegisterRepo(repo string, actions []string, workflows []string) error {
	return a.flowFacade.RegisterRepo(repo, actions, workflows)
}

func (a *actorImpl) RunRepoFlows(repo string, token string) error {
	return a.flowFacade.TriggerRepoFlows(repo, token)
}

func (a *actorImpl) RunCustomFlow(repo string, flowType string, name string, token string, params map[string]string) error {
	return a.flowFacade.TriggerCustomFlow(repo, flowType, name, token, params)
}
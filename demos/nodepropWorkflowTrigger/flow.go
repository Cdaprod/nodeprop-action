package flow

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
)

// WorkflowTrigger defines the interface for triggering workflows.
type WorkflowTrigger interface {
	Trigger(target string, params map[string]string, authToken string) error
}

// TriggerManager handles actions and workflows.
type TriggerManager struct {
	Actions   map[string]ActionTrigger
	Workflows map[string]WorkflowTrigger
	mu        sync.Mutex
}

var instance *TriggerManager
var once sync.Once

// GetTriggerManager returns a singleton instance of TriggerManager.
func GetTriggerManager() *TriggerManager {
	once.Do(func() {
		instance = &TriggerManager{
			Actions:   make(map[string]ActionTrigger),
			Workflows: make(map[string]WorkflowTrigger),
		}
	})
	return instance
}

// RegisterAction registers a new action trigger.
func (tm *TriggerManager) RegisterAction(name string, trigger ActionTrigger) {
	tm.mu.Lock()
	defer tm.mu.Unlock()
	tm.Actions[name] = trigger
}

// RegisterWorkflow registers a new workflow trigger.
func (tm *TriggerManager) RegisterWorkflow(name string, trigger WorkflowTrigger) {
	tm.mu.Lock()
	defer tm.mu.Unlock()
	tm.Workflows[name] = trigger
}

// ExecuteAction executes a registered action.
func (tm *TriggerManager) ExecuteAction(name, target, token string, params map[string]string) error {
	tm.mu.Lock()
	trigger, exists := tm.Actions[name]
	tm.mu.Unlock()

	if !exists {
		return fmt.Errorf("action %s not registered", name)
	}
	return trigger.Trigger(target, params, token)
}

// ExecuteWorkflow executes a registered workflow.
func (tm *TriggerManager) ExecuteWorkflow(name, target, token string, params map[string]string) error {
	tm.mu.Lock()
	trigger, exists := tm.Workflows[name]
	tm.mu.Unlock()

	if !exists {
		return fmt.Errorf("workflow %s not registered", name)
	}
	return trigger.Trigger(target, params, token)
}

// ActionTrigger represents a trigger for GitHub Actions.
type ActionTrigger struct {
	ActionName string
	Ref        string
}

func (a *ActionTrigger) Trigger(target string, params map[string]string, authToken string) error {
	url := fmt.Sprintf("https://api.github.com/repos/%s/dispatches", a.ActionName)
	payload := map[string]interface{}{
		"ref":    a.Ref,
		"inputs": params,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %v", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+authToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to trigger action: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 204 {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	return nil
}

// WorkflowTrigger represents a trigger for GitHub reusable workflows.
type WorkflowTrigger struct {
	WorkflowFile string
	Ref          string
}

func (w *WorkflowTrigger) Trigger(target string, params map[string]string, authToken string) error {
	url := fmt.Sprintf("https://api.github.com/repos/%s/actions/workflows/%s/dispatches", target, w.WorkflowFile)
	payload := map[string]interface{}{
		"ref":    w.Ref,
		"inputs": params,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %v", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+authToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to trigger workflow: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 204 {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	return nil
}
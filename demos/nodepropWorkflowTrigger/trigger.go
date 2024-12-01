package flow

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

// WorkflowTrigger defines the interface for triggering workflows.
type WorkflowTrigger interface {
	TriggerWorkflow(target string, params map[string]string, authToken string) error
}

// TriggerWorkflowSystem provides a generic way to execute a workflow through a WorkflowTrigger.
func TriggerWorkflowSystem(trigger WorkflowTrigger, target string, params map[string]string, token string) error {
	return trigger.TriggerWorkflow(target, params, token)
}

// GitHubWorkflowTrigger implements the WorkflowTrigger interface for GitHub Actions.
type GitHubWorkflowTrigger struct{}

// TriggerWorkflow triggers a GitHub Actions workflow in the specified repository.
func (g *GitHubWorkflowTrigger) TriggerWorkflow(target string, params map[string]string, authToken string) error {
	// Construct the URL for the GitHub API
	url := fmt.Sprintf("https://api.github.com/repos/%s/actions/workflows/%s/dispatches", target, params["workflow_id"])

	// Prepare the payload for the API request
	payload := map[string]interface{}{
		"ref":    params["ref"],
		"inputs": params["inputs"],
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal payload: %v", err)
	}

	// Build the HTTP request
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Authorization", "Bearer "+authToken)
	req.Header.Set("Content-Type", "application/json")

	// Send the request
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to trigger workflow: %v", err)
	}
	defer resp.Body.Close()

	// Check the response status
	if resp.StatusCode != 204 {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	return nil
}

// triggerNodeProp is a concrete implementation for triggering the NodeProp workflow on GitHub.
func triggerNodeProp(repo string, token string) error {
	// Create an instance of the GitHubWorkflowTrigger
	trigger := &GitHubWorkflowTrigger{}

	// Define the parameters for the workflow
	params := map[string]string{
		"workflow_id": "nodeprop-action.yml", // The workflow ID or filename
		"ref":         "main",               // Branch or tag to trigger on
		"inputs":      "{}",                 // Workflow-specific inputs in JSON format
	}

	// Trigger the workflow
	return trigger.TriggerWorkflow(repo, params, token)
}
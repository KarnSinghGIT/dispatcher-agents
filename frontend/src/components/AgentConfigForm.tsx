import React from 'react';
import type { AgentConfig } from '../types';
import './AgentConfigForm.css';

interface AgentConfigFormProps {
  agent: AgentConfig;
  label: string;
  onChange: (agent: AgentConfig) => void;
}

export const AgentConfigForm: React.FC<AgentConfigFormProps> = ({ agent, label, onChange }) => {
  const handleChange = (field: keyof AgentConfig, value: string) => {
    onChange({ ...agent, [field]: value });
  };

  return (
    <div className="agent-config-form">
      <h2>{label}</h2>
      
      <div className="form-group">
        <label htmlFor={`${agent.role}-prompt`}>Agent Prompt</label>
        <textarea
          id={`${agent.role}-prompt`}
          rows={15}
          value={agent.prompt}
          onChange={(e) => handleChange('prompt', e.target.value)}
          placeholder={`Enter the prompt for the ${agent.role} agent...`}
        />
      </div>

      <div className="form-group">
        <label htmlFor={`${agent.role}-notes`}>Acting Notes (Optional)</label>
        <textarea
          id={`${agent.role}-notes`}
          rows={3}
          value={agent.actingNotes || ''}
          onChange={(e) => handleChange('actingNotes', e.target.value)}
          placeholder="Optional notes to guide agent behavior..."
        />
      </div>
    </div>
  );
};


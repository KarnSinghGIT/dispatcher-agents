import React from 'react';
import type { Scenario } from '../types';
import './ScenarioForm.css';

interface ScenarioFormProps {
  scenario: Scenario;
  onChange: (scenario: Scenario) => void;
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({ scenario, onChange }) => {
  const handleChange = (field: keyof Scenario, value: string | number) => {
    onChange({ ...scenario, [field]: value });
  };

  return (
    <div className="scenario-form">
      <h2>Load Scenario</h2>
      
      <div className="form-group">
        <label htmlFor="loadId">Load ID</label>
        <input
          id="loadId"
          type="text"
          value={scenario.loadId}
          onChange={(e) => handleChange('loadId', e.target.value)}
          placeholder="HDX-2478"
        />
      </div>

      <div className="form-group">
        <label htmlFor="loadType">Load Type</label>
        <input
          id="loadType"
          type="text"
          value={scenario.loadType}
          onChange={(e) => handleChange('loadType', e.target.value)}
          placeholder="HVAC units"
        />
      </div>

      <div className="form-group">
        <label htmlFor="weight">Weight (lbs)</label>
        <input
          id="weight"
          type="number"
          value={scenario.weight}
          onChange={(e) => handleChange('weight', parseInt(e.target.value) || 0)}
          placeholder="42000"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="pickupLocation">Pickup Location</label>
          <input
            id="pickupLocation"
            type="text"
            value={scenario.pickupLocation}
            onChange={(e) => handleChange('pickupLocation', e.target.value)}
            placeholder="Dallas TX"
          />
        </div>
        <div className="form-group">
          <label htmlFor="pickupTime">Pickup Time</label>
          <input
            id="pickupTime"
            type="text"
            value={scenario.pickupTime}
            onChange={(e) => handleChange('pickupTime', e.target.value)}
            placeholder="8 AM"
          />
        </div>
        <div className="form-group">
          <label htmlFor="pickupType">Pickup Type</label>
          <input
            id="pickupType"
            type="text"
            value={scenario.pickupType}
            onChange={(e) => handleChange('pickupType', e.target.value)}
            placeholder="live"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="deliveryLocation">Delivery Location</label>
          <input
            id="deliveryLocation"
            type="text"
            value={scenario.deliveryLocation}
            onChange={(e) => handleChange('deliveryLocation', e.target.value)}
            placeholder="Atlanta GA"
          />
        </div>
        <div className="form-group">
          <label htmlFor="deliveryDeadline">Delivery Deadline</label>
          <input
            id="deliveryDeadline"
            type="text"
            value={scenario.deliveryDeadline}
            onChange={(e) => handleChange('deliveryDeadline', e.target.value)}
            placeholder="before noon next day"
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="trailerType">Trailer Type</label>
        <input
          id="trailerType"
          type="text"
          value={scenario.trailerType}
          onChange={(e) => handleChange('trailerType', e.target.value)}
          placeholder="dry-van"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="ratePerMile">Rate per Mile ($)</label>
          <input
            id="ratePerMile"
            type="number"
            step="0.01"
            value={scenario.ratePerMile}
            onChange={(e) => handleChange('ratePerMile', parseFloat(e.target.value) || 0)}
            placeholder="2.10"
          />
        </div>
        <div className="form-group">
          <label htmlFor="totalRate">Total Rate ($)</label>
          <input
            id="totalRate"
            type="number"
            value={scenario.totalRate}
            onChange={(e) => handleChange('totalRate', parseFloat(e.target.value) || 0)}
            placeholder="1680"
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="accessorials">Accessorials</label>
        <input
          id="accessorials"
          type="text"
          value={scenario.accessorials}
          onChange={(e) => handleChange('accessorials', e.target.value)}
          placeholder="none"
        />
      </div>

      <div className="form-group">
        <label htmlFor="securementRequirements">Securement Requirements</label>
        <input
          id="securementRequirements"
          type="text"
          value={scenario.securementRequirements}
          onChange={(e) => handleChange('securementRequirements', e.target.value)}
          placeholder="two-strap securement"
        />
      </div>

      <div className="form-group">
        <label htmlFor="tmsUpdate">TMS Update</label>
        <input
          id="tmsUpdate"
          type="text"
          value={scenario.tmsUpdate}
          onChange={(e) => handleChange('tmsUpdate', e.target.value)}
          placeholder="Macro-1 update when empty"
        />
      </div>
    </div>
  );
};


import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, Badge, ProgressBar, Tab, Tabs } from 'react-bootstrap';
import axios from 'axios';
import StudyResults from './components/StudyResults';
import ServiceStatus from './components/ServiceStatus';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8250';

function App() {
  const [formData, setFormData] = useState({
    protocol_text: '',
    disease_area: '',
    target_countries: [],
    target_enrollment: 100,
    inclusion_criteria: [],
    exclusion_criteria: [],
    study_duration_months: 12,
    primary_endpoints: [],
    secondary_endpoints: []
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleArrayInput = (field, value) => {
    const items = value.split('\n').filter(item => item.trim());
    setFormData(prev => ({
      ...prev,
      [field]: items
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/plan_rwe_study`, formData);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while processing your request');
    } finally {
      setLoading(false);
    }
  };

  const sampleProtocol = `This is a Phase III, randomized, double-blind, placebo-controlled study to evaluate the efficacy and safety of Drug X in patients with Type 2 Diabetes Mellitus. 

The study will enroll approximately 500 patients across 50 sites globally. Patients will be randomized 1:1 to receive either Drug X 10mg once daily or matching placebo for 52 weeks.

Primary Endpoint: Change from baseline in HbA1c at Week 52
Secondary Endpoints: 
- Change from baseline in fasting plasma glucose
- Proportion of patients achieving HbA1c <7.0%
- Change from baseline in body weight

Key Inclusion Criteria:
- Type 2 diabetes mellitus diagnosis ≥6 months
- HbA1c 7.0-10.0% at screening
- Age 18-75 years
- BMI 25-40 kg/m²

Key Exclusion Criteria:
- Type 1 diabetes
- eGFR <45 mL/min/1.73m²
- Recent cardiovascular event (<3 months)
- Pregnancy or lactation`;

  const loadSampleData = () => {
    setFormData({
      protocol_text: sampleProtocol,
      disease_area: 'Type 2 Diabetes Mellitus',
      target_countries: ['USA', 'UK', 'Germany', 'Japan'],
      target_enrollment: 500,
      inclusion_criteria: [
        'Type 2 diabetes diagnosis ≥6 months',
        'HbA1c 7.0-10.0% at screening',
        'Age 18-75 years',
        'BMI 25-40 kg/m²'
      ],
      exclusion_criteria: [
        'Type 1 diabetes',
        'eGFR <45 mL/min/1.73m²',
        'Recent cardiovascular event (<3 months)',
        'Pregnancy or lactation'
      ],
      study_duration_months: 12,
      primary_endpoints: ['Change from baseline in HbA1c at Week 52'],
      secondary_endpoints: [
        'Change from baseline in fasting plasma glucose',
        'Proportion of patients achieving HbA1c <7.0%',
        'Change from baseline in body weight'
      ]
    });
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>Global RWE Study Planner</h1>
        <p className="lead">Comprehensive Real-World Evidence study design and site selection tool</p>
      </div>

      <Container fluid>
        <Row>
          <Col lg={4}>
            <Card className="mb-4">
              <Card.Header>
                <h5>Study Parameters</h5>
                <Button variant="link" size="sm" onClick={loadSampleData}>
                  Load Sample Data
                </Button>
              </Card.Header>
              <Card.Body>
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label>Protocol Text</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={5}
                      name="protocol_text"
                      value={formData.protocol_text}
                      onChange={handleInputChange}
                      placeholder="Enter protocol summary..."
                      required
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Disease Area</Form.Label>
                    <Form.Control
                      type="text"
                      name="disease_area"
                      value={formData.disease_area}
                      onChange={handleInputChange}
                      placeholder="e.g., Type 2 Diabetes"
                      required
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Target Countries (one per line)</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      value={formData.target_countries.join('\n')}
                      onChange={(e) => handleArrayInput('target_countries', e.target.value)}
                      placeholder="USA&#10;UK&#10;Germany"
                      required
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Target Enrollment</Form.Label>
                    <Form.Control
                      type="number"
                      name="target_enrollment"
                      value={formData.target_enrollment}
                      onChange={handleInputChange}
                      min="10"
                      required
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Study Duration (months)</Form.Label>
                    <Form.Control
                      type="number"
                      name="study_duration_months"
                      value={formData.study_duration_months}
                      onChange={handleInputChange}
                      min="1"
                      required
                    />
                  </Form.Group>

                  <Tabs defaultActiveKey="criteria" className="mb-3">
                    <Tab eventKey="criteria" title="Criteria">
                      <Form.Group className="mb-3">
                        <Form.Label>Inclusion Criteria (one per line)</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={4}
                          value={formData.inclusion_criteria.join('\n')}
                          onChange={(e) => handleArrayInput('inclusion_criteria', e.target.value)}
                          placeholder="Age 18-75 years&#10;HbA1c 7.0-10.0%"
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>Exclusion Criteria (one per line)</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={4}
                          value={formData.exclusion_criteria.join('\n')}
                          onChange={(e) => handleArrayInput('exclusion_criteria', e.target.value)}
                          placeholder="Type 1 diabetes&#10;Pregnancy"
                        />
                      </Form.Group>
                    </Tab>

                    <Tab eventKey="endpoints" title="Endpoints">
                      <Form.Group className="mb-3">
                        <Form.Label>Primary Endpoints (one per line)</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={3}
                          value={formData.primary_endpoints.join('\n')}
                          onChange={(e) => handleArrayInput('primary_endpoints', e.target.value)}
                          placeholder="Change in HbA1c at Week 52"
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>Secondary Endpoints (one per line)</Form.Label>
                        <Form.Control
                          as="textarea"
                          rows={3}
                          value={formData.secondary_endpoints.join('\n')}
                          onChange={(e) => handleArrayInput('secondary_endpoints', e.target.value)}
                          placeholder="Change in body weight"
                        />
                      </Form.Group>
                    </Tab>
                  </Tabs>

                  <Button 
                    variant="primary" 
                    type="submit" 
                    disabled={loading}
                    className="w-100"
                  >
                    {loading ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        Analyzing Study...
                      </>
                    ) : (
                      'Plan RWE Study'
                    )}
                  </Button>
                </Form>
              </Card.Body>
            </Card>

            <ServiceStatus apiUrl={API_URL} />
          </Col>

          <Col lg={8}>
            {error && (
              <Alert variant="danger" dismissible onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            {loading && (
              <Card>
                <Card.Body>
                  <div className="loading-spinner">
                    <div className="text-center">
                      <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
                      <p className="mt-3">Analyzing protocol and identifying optimal sites...</p>
                      <ProgressBar animated now={45} className="mt-2" />
                    </div>
                  </div>
                </Card.Body>
              </Card>
            )}

            {results && !loading && (
              <StudyResults results={results} />
            )}

            {!results && !loading && (
              <Card>
                <Card.Body className="text-center py-5">
                  <h5>Welcome to the RWE Study Planner</h5>
                  <p>Enter your study parameters on the left to get started</p>
                  <p className="text-muted">Or click "Load Sample Data" to see an example</p>
                </Card.Body>
              </Card>
            )}
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
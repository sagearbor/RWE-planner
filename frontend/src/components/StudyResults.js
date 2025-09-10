import React from 'react';
import { Card, Row, Col, Badge, ListGroup, ProgressBar, Alert } from 'react-bootstrap';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

function StudyResults({ results }) {
  const getScoreClass = (score) => {
    if (score < 5) return 'score-low';
    if (score < 7) return 'score-medium';
    return 'score-high';
  };

  const getScoreVariant = (score) => {
    if (score < 5) return 'success';
    if (score < 7) return 'warning';
    return 'danger';
  };

  const siteChartData = {
    labels: results.recommended_sites.slice(0, 5).map(site => site.site_name),
    datasets: [
      {
        label: 'Feasibility Score',
        data: results.recommended_sites.slice(0, 5).map(site => site.feasibility_score),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
      {
        label: 'Diversity Score',
        data: results.recommended_sites.slice(0, 5).map(site => site.diversity_score),
        backgroundColor: 'rgba(255, 206, 86, 0.6)',
      },
      {
        label: 'Data Availability',
        data: results.recommended_sites.slice(0, 5).map(site => site.data_availability_score),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      }
    ]
  };

  const complexityChartData = {
    labels: ['Protocol Complexity'],
    datasets: [{
      data: [results.protocol_complexity_score, 10 - results.protocol_complexity_score],
      backgroundColor: [
        results.protocol_complexity_score < 5 ? '#28a745' : 
        results.protocol_complexity_score < 7 ? '#ffc107' : '#dc3545',
        '#e9ecef'
      ],
      borderWidth: 0
    }]
  };

  return (
    <div>
      <Row className="mb-4">
        <Col md={6}>
          <Card className="score-card">
            <Card.Body>
              <h5>Protocol Complexity</h5>
              <div className="d-flex align-items-center">
                <div style={{ width: '120px', height: '120px' }}>
                  <Doughnut 
                    data={complexityChartData} 
                    options={{ 
                      plugins: { legend: { display: false } },
                      cutout: '70%'
                    }} 
                  />
                </div>
                <div className="ms-3">
                  <div className={`score-badge ${getScoreClass(results.protocol_complexity_score)}`}>
                    {results.protocol_complexity_score}/10
                  </div>
                  <Badge bg={getScoreVariant(results.protocol_complexity_score)} className="mt-2">
                    {results.protocol_complexity_score < 5 ? 'Low Complexity' :
                     results.protocol_complexity_score < 7 ? 'Moderate Complexity' : 'High Complexity'}
                  </Badge>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="score-card">
            <Card.Body>
              <h5>Estimated Cohort Size</h5>
              <div className="display-4 text-primary">
                {results.estimated_total_cohort_size.toLocaleString()}
              </div>
              <p className="text-muted">Potential patients available</p>
              <ProgressBar 
                now={(results.estimated_total_cohort_size / 100000) * 100} 
                label={`${Math.round((results.estimated_total_cohort_size / 100000) * 100)}%`}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {results.risk_factors && results.risk_factors.length > 0 && (
        <Alert variant="warning">
          <Alert.Heading>Risk Factors Identified</Alert.Heading>
          <ul className="mb-0">
            {results.risk_factors.map((risk, index) => (
              <li key={index}>{risk}</li>
            ))}
          </ul>
        </Alert>
      )}

      <Card className="mb-4">
        <Card.Header>
          <h5>Top Recommended Sites</h5>
        </Card.Header>
        <Card.Body>
          <div style={{ height: '300px', marginBottom: '20px' }}>
            <Bar 
              data={siteChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 10
                  }
                }
              }}
            />
          </div>

          <ListGroup>
            {results.recommended_sites.slice(0, 5).map((site, index) => (
              <ListGroup.Item key={site.site_id} className="site-card">
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <h6>
                      <Badge bg="primary" className="me-2">#{site.overall_rank}</Badge>
                      {site.site_name}
                    </h6>
                    <p className="text-muted mb-2">{site.country}</p>
                    
                    <div className="mb-2">
                      <small className="text-muted">Feasibility</small>
                      <ProgressBar now={site.feasibility_score * 10} variant="info" className="mb-1" style={{ height: '10px' }} />
                      
                      <small className="text-muted">Diversity</small>
                      <ProgressBar now={site.diversity_score * 10} variant="warning" className="mb-1" style={{ height: '10px' }} />
                      
                      <small className="text-muted">Data Availability</small>
                      <ProgressBar now={site.data_availability_score * 10} variant="success" style={{ height: '10px' }} />
                    </div>

                    {site.strengths && site.strengths.length > 0 && (
                      <div className="mb-2">
                        <small className="text-success">
                          <strong>Strengths:</strong> {site.strengths.join(', ')}
                        </small>
                      </div>
                    )}
                    
                    {site.challenges && site.challenges.length > 0 && (
                      <div>
                        <small className="text-warning">
                          <strong>Challenges:</strong> {site.challenges.join(', ')}
                        </small>
                      </div>
                    )}
                  </div>
                  
                  <div className="text-end">
                    <Badge bg="secondary" className="p-2">
                      Overall Score<br/>
                      <span className="h5">
                        {((site.feasibility_score + site.diversity_score + site.data_availability_score) / 3).toFixed(1)}
                      </span>
                    </Badge>
                  </div>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Card.Body>
      </Card>

      {results.optimization_opportunities && results.optimization_opportunities.length > 0 && (
        <Card>
          <Card.Header>
            <h5>Optimization Opportunities</h5>
          </Card.Header>
          <Card.Body>
            <ListGroup variant="flush">
              {results.optimization_opportunities.map((opportunity, index) => (
                <ListGroup.Item key={index}>
                  <i className="bi bi-lightbulb me-2"></i>
                  {opportunity}
                </ListGroup.Item>
              ))}
            </ListGroup>
          </Card.Body>
        </Card>
      )}
    </div>
  );
}

export default StudyResults;
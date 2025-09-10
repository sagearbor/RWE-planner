import React, { useState, useEffect } from 'react';
import { Card, ListGroup, Badge, Button, Spinner } from 'react-bootstrap';
import axios from 'axios';

function ServiceStatus({ apiUrl }) {
  const [services, setServices] = useState({});
  const [loading, setLoading] = useState(false);

  const checkServices = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiUrl}/service_status`);
      setServices(response.data);
    } catch (error) {
      console.error('Failed to check service status:', error);
      setServices({});
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkServices();
  }, [apiUrl]);

  const getStatusBadge = (status) => {
    switch(status) {
      case 'healthy':
        return <Badge bg="success">Online</Badge>;
      case 'unhealthy':
        return <Badge bg="warning">Unhealthy</Badge>;
      case 'unreachable':
        return <Badge bg="danger">Offline</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  const serviceDisplayNames = {
    'data_ingestor': 'Data Ingestor',
    'ehr_connector': 'EHR Connector',
    'claims_parser': 'Claims Parser',
    'feasibility_predictor': 'Site Feasibility',
    'diversity_mapper': 'Diversity Mapper',
    'protocol_scorer': 'Protocol Scorer',
    'soa_comparator': 'SoA Comparator'
  };

  return (
    <Card>
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h6 className="mb-0">MCP Services</h6>
        <Button 
          size="sm" 
          variant="outline-primary" 
          onClick={checkServices}
          disabled={loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : 'Refresh'}
        </Button>
      </Card.Header>
      <ListGroup variant="flush">
        {Object.entries(services).map(([service, status]) => (
          <ListGroup.Item key={service} className="d-flex justify-content-between align-items-center py-2">
            <small>{serviceDisplayNames[service] || service}</small>
            {getStatusBadge(status)}
          </ListGroup.Item>
        ))}
        {Object.keys(services).length === 0 && !loading && (
          <ListGroup.Item className="text-center text-muted py-3">
            <small>No services detected</small>
          </ListGroup.Item>
        )}
      </ListGroup>
    </Card>
  );
}

export default ServiceStatus;
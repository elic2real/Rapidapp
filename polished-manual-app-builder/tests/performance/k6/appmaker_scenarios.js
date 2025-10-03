import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 500,
  duration: '5m',
  thresholds: {
    http_req_duration: ['p(95)<200'],
    errors: ['rate<0.01'],
  },
};

export default function () {
  const res = http.post('http://localhost:3000/api/generate', JSON.stringify({ prompt: 'CRUD app' }), { headers: { 'Content-Type': 'application/json' } });
  check(res, {
    'status is 200': (r) => r.status === 200,
    'no error in body': (r) => !r.body.includes('error'),
  });
  sleep(1);
}

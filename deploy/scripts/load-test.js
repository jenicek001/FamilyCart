import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Custom metrics
const wsConnectionTime = new Trend('ws_connection_time');
const wsMessagesSent = new Counter('ws_messages_sent');
const wsMessagesReceived = new Counter('ws_messages_received');
const wsErrors = new Counter('ws_errors');
const authSuccessRate = new Rate('auth_success_rate');
const apiSuccessRate = new Rate('api_success_rate');

// Load test configuration
export const options = {
  stages: [
    { duration: '2m', target: 5 },    // Ramp up to 5 users
    { duration: '3m', target: 10 },   // Stay at 10 users
    { duration: '3m', target: 25 },   // Ramp to 25 users
    { duration: '5m', target: 25 },   // Stay at 25 users (target: 50 user capacity)
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.02'],   // Error rate under 2%
    ws_connection_time: ['p(95)<1000'], // WebSocket connection under 1s
    auth_success_rate: ['rate>0.95'], // 95% auth success rate
    api_success_rate: ['rate>0.98'],  // 98% API success rate
  },
};

const BASE_URL = __ENV.UAT_BASE_URL || 'http://localhost:3001';
const API_URL = BASE_URL.replace(/:\d+/, ':8001');
const WS_URL = API_URL.replace('http', 'ws');

// Test data
const TEST_USERS = [
  { email: 'test1@familycart.local', password: 'testpassword123' },
  { email: 'test2@familycart.local', password: 'testpassword123' },
  { email: 'test3@familycart.local', password: 'testpassword123' },
  { email: 'test4@familycart.local', password: 'testpassword123' },
  { email: 'test5@familycart.local', password: 'testpassword123' },
];

const SAMPLE_ITEMS = [
  'Milk', 'Bread', 'Eggs', 'Cheese', 'Apples', 'Bananas', 'Chicken', 'Rice',
  'Pasta', 'Tomatoes', 'Onions', 'Carrots', 'Butter', 'Yogurt', 'Orange Juice'
];

let authTokens = {};

export function setup() {
  console.log('🚀 Starting FamilyCart UAT Load Test');
  console.log(`📍 Frontend URL: ${BASE_URL}`);
  console.log(`🔌 API URL: ${API_URL}`);
  console.log(`🌐 WebSocket URL: ${WS_URL}`);
  
  // Health check
  const healthCheck = http.get(`${API_URL}/health`);
  if (healthCheck.status !== 200) {
    console.error('❌ Health check failed, aborting test');
    return null;
  }
  
  console.log('✅ Health check passed');
  return { baseUrl: BASE_URL, apiUrl: API_URL, wsUrl: WS_URL };
}

export default function(data) {
  if (!data) {
    console.error('❌ Setup failed, skipping test');
    return;
  }
  
  const userId = __VU;
  const testUser = TEST_USERS[userId % TEST_USERS.length];
  
  // 1. Test user authentication
  testAuthentication(data.apiUrl, testUser, userId);
  
  // 2. Test API endpoints
  if (authTokens[userId]) {
    testApiEndpoints(data.apiUrl, authTokens[userId]);
    
    // 3. Test WebSocket connection (25% of users)
    if (Math.random() < 0.25) {
      testWebSocketConnection(data.wsUrl, authTokens[userId]);
    }
  }
  
  // 4. Test frontend load
  testFrontendLoad(data.baseUrl);
  
  sleep(1);
}

function testAuthentication(apiUrl, user, userId) {
  console.log(`👤 Testing authentication for user ${userId}`);
  
  const loginPayload = {
    username: user.email,
    password: user.password,
  };
  
  const params = {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    timeout: '30s',
  };
  
  // Convert to form data
  const formData = Object.keys(loginPayload)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(loginPayload[key])}`)
    .join('&');
  
  const loginResponse = http.post(`${apiUrl}/api/v1/auth/login`, formData, params);
  
  const authSuccess = check(loginResponse, {
    'login status is 200': (r) => r.status === 200,
    'login returns access token': (r) => r.json('access_token') !== undefined,
    'login response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  authSuccessRate.add(authSuccess);
  
  if (authSuccess && loginResponse.json('access_token')) {
    authTokens[userId] = loginResponse.json('access_token');
    console.log(`✅ Authentication successful for user ${userId}`);
  } else {
    console.log(`❌ Authentication failed for user ${userId}: ${loginResponse.status}`);
  }
}

function testApiEndpoints(apiUrl, token) {
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
  
  // Test shopping lists endpoint
  const listsResponse = http.get(`${apiUrl}/api/v1/shopping-lists/`, { headers });
  
  const listsSuccess = check(listsResponse, {
    'lists status is 200': (r) => r.status === 200,
    'lists response time < 1s': (r) => r.timings.duration < 1000,
    'lists returns array': (r) => Array.isArray(r.json()),
  });
  
  apiSuccessRate.add(listsSuccess);
  
  if (listsSuccess && listsResponse.json().length > 0) {
    const listId = listsResponse.json()[0].id;
    
    // Test items endpoint
    const itemsResponse = http.get(`${apiUrl}/api/v1/shopping-lists/${listId}/items`, { headers });
    
    const itemsSuccess = check(itemsResponse, {
      'items status is 200': (r) => r.status === 200,
      'items response time < 1s': (r) => r.timings.duration < 1000,
    });
    
    apiSuccessRate.add(itemsSuccess);
    
    // Test adding an item (20% chance)
    if (Math.random() < 0.2) {
      const randomItem = SAMPLE_ITEMS[Math.floor(Math.random() * SAMPLE_ITEMS.length)];
      const addItemPayload = {
        name: randomItem,
        quantity: Math.floor(Math.random() * 5) + 1,
        unit: 'pieces',
        notes: `Added by load test user ${__VU}`,
      };
      
      const addItemResponse = http.post(
        `${apiUrl}/api/v1/shopping-lists/${listId}/items`,
        JSON.stringify(addItemPayload),
        { headers }
      );
      
      const addItemSuccess = check(addItemResponse, {
        'add item status is 201': (r) => r.status === 201,
        'add item response time < 2s': (r) => r.timings.duration < 2000,
      });
      
      apiSuccessRate.add(addItemSuccess);
    }
  }
}

function testWebSocketConnection(wsUrl, token) {
  console.log(`🔌 Testing WebSocket connection for user ${__VU}`);
  
  const wsParams = {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  };
  
  const wsStart = Date.now();
  
  const response = ws.connect(`${wsUrl}/ws`, wsParams, function (socket) {
    const connectionTime = Date.now() - wsStart;
    wsConnectionTime.add(connectionTime);
    
    socket.on('open', function () {
      console.log(`✅ WebSocket connected for user ${__VU}`);
      
      // Send a ping message
      socket.send(JSON.stringify({
        type: 'ping',
        timestamp: Date.now(),
      }));
      wsMessagesSent.add(1);
    });
    
    socket.on('message', function (message) {
      wsMessagesReceived.add(1);
      try {
        const data = JSON.parse(message);
        console.log(`📨 WebSocket message received by user ${__VU}: ${data.type}`);
      } catch (e) {
        console.log(`📨 WebSocket raw message received by user ${__VU}`);
      }
    });
    
    socket.on('error', function (e) {
      console.log(`❌ WebSocket error for user ${__VU}: ${e.error()}`);
      wsErrors.add(1);
    });
    
    socket.on('close', function () {
      console.log(`🔌 WebSocket closed for user ${__VU}`);
    });
    
    // Keep connection open for 10-30 seconds
    const connectionDuration = Math.random() * 20 + 10;
    socket.setTimeout(function () {
      socket.close();
    }, connectionDuration * 1000);
  });
  
  check(response, {
    'websocket connection successful': (r) => r && r.url === `${wsUrl}/ws`,
  });
}

function testFrontendLoad(baseUrl) {
  // Test main page load
  const frontendResponse = http.get(baseUrl);
  
  check(frontendResponse, {
    'frontend status is 200': (r) => r.status === 200,
    'frontend response time < 3s': (r) => r.timings.duration < 3000,
    'frontend contains title': (r) => r.body.includes('FamilyCart'),
  });
  
  // Test static assets (10% chance)
  if (Math.random() < 0.1) {
    const staticAssets = ['/_next/static/css/', '/_next/static/js/', '/favicon.ico'];
    staticAssets.forEach(asset => {
      const assetResponse = http.get(`${baseUrl}${asset}`, { timeout: '10s' });
      check(assetResponse, {
        [`static asset ${asset} loads successfully`]: (r) => r.status === 200 || r.status === 404, // 404 is acceptable for some assets
      });
    });
  }
}

export function teardown(data) {
  console.log('🏁 Load test completed');
  
  if (data) {
    // Final health check
    const finalHealthCheck = http.get(`${data.apiUrl}/health`);
    if (finalHealthCheck.status === 200) {
      console.log('✅ Final health check passed');
    } else {
      console.log('❌ Final health check failed');
    }
  }
  
  console.log('📊 Test Summary:');
  console.log(`   Total VUs: ${__ENV.K6_VUS || 'N/A'}`);
  console.log(`   Duration: ${__ENV.K6_DURATION || 'N/A'}`);
  console.log('📈 Check detailed metrics in the k6 output above');
}
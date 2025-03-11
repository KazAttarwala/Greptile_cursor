import { createServer, Model } from 'miragejs';

export function makeServer({ environment = 'development' } = {}) {
  let server = createServer({
    environment,
    
    models: {
      repo: Model,
      changelog: Model,
    },
    
    seeds(server) {
      server.create('repo', { id: 'repo1', name: 'frontend/main-app' });
      server.create('repo', { id: 'repo2', name: 'backend/api-service' });
      server.create('repo', { id: 'repo3', name: 'mobile/ios-app' });
      
      server.create('changelog', {
        id: 'repo1',
        repo: 'frontend/main-app',
        generated_at: '2024-03-20T12:00:00Z',
        changes: {
          '2024-03-20': [
            {
              pr_number: 123,
              pr_url: 'https://github.com/example/repo/pull/123',
              author: 'dev1',
              summary: 'Added user authentication system',
              details: 'Implemented login, registration, and password reset functionality',
              type: 'feature'
            },
            {
              pr_number: 124,
              pr_url: 'https://github.com/example/repo/pull/124',
              author: 'dev2',
              summary: 'Fixed responsive layout issues on mobile devices',
              details: 'Resolved navbar and sidebar display problems on small screens',
              type: 'bugfix'
            }
          ],
          '2024-03-15': [
            {
              pr_number: 120,
              pr_url: 'https://github.com/example/repo/pull/120',
              author: 'dev3',
              summary: 'Improved performance of data loading',
              details: 'Optimized API calls and implemented caching',
              type: 'improvement'
            }
          ],
          '2024-03-10': [
            {
              pr_number: 115,
              pr_url: 'https://github.com/example/repo/pull/115',
              author: 'dev1',
              summary: 'Updated documentation for API endpoints',
              details: 'Added examples and improved clarity of API documentation'
            }
          ]
        },
        categories: {
          'Features': [123],
          'Bug Fixes': [124],
          'Improvements': [120]
        }
      });
    }
  });
} 
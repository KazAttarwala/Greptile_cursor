// This would be replaced with actual API endpoints in a real implementation
const API_BASE_URL = 'http://localhost:5000/api';

// Fetch list of available repositories
export async function fetchRepos() {
  try {
    const response = await fetch(`${API_BASE_URL}/repos`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch repositories');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching repositories:', error);
    throw error;
  }
}

// Fetch changelog for a specific repository
export async function fetchChangelog(repoId) {
  try {
    const response = await fetch(`${API_BASE_URL}/repos/${repoId}/changelog`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch changelog');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching changelog:', error);
    throw error;
  }
}

// Add a new repository
export async function addRepository(repoData) {
  try {
    const response = await fetch(`${API_BASE_URL}/repos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(repoData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to add repository');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error adding repository:', error);
    throw error;
  }
}

// Delete a repository
export async function deleteRepository(repoId) {
  try {
    const response = await fetch(`${API_BASE_URL}/repos/${repoId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete repository');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error deleting repository:', error);
    throw error;
  }
}

// Add a new changelog entry
export async function addChangelogEntry(repoId, date, entry) {
  try {
    const response = await fetch(`${API_BASE_URL}/repos/${repoId}/entries`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ date, entry }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to add changelog entry');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error adding changelog entry:', error);
    throw error;
  }
}

// For development/demo purposes, we can use mock data
export async function fetchMockData() {
  // This simulates API latency
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return {
    repos: [
      { id: 'repo1', name: 'frontend/main-app' },
      { id: 'repo2', name: 'backend/api-service' },
      { id: 'repo3', name: 'mobile/ios-app' }
    ],
    changelogs: {
      repo1: {
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
          ]
        },
        categories: {
          'Features': [123],
          'Bug Fixes': [124],
          'Improvements': [120]
        }
      }
      // Add more mock data for other repos as needed
    }
  };
} 
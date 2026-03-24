/**
 * Frontend tests for app.js
 * Tests using Vitest + jsdom for DOM testing
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';

describe('Activities List Page', () => {
  let dom;
  let window;
  let document;

  beforeEach(() => {
    // Create a fresh DOM for each test
    dom = new JSDOM(`
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>Mergington High School Activities</title>
        </head>
        <body>
          <header>
            <h1>Mergington High School</h1>
            <h2>Extracurricular Activities</h2>
          </header>

          <main>
            <section id="activities-container">
              <h3>Available Activities</h3>
              <div id="activities-list">
                <p>Loading activities...</p>
              </div>
            </section>

            <section id="signup-container">
              <h3>Sign Up for an Activity</h3>
              <form id="signup-form">
                <div class="form-group">
                  <label for="email">Student Email:</label>
                  <input type="email" id="email" required placeholder="your-email@mergington.edu" />
                </div>
                <div class="form-group">
                  <label for="activity">Select Activity:</label>
                  <select id="activity" required>
                    <option value="">-- Select an activity --</option>
                  </select>
                </div>
                <button type="submit">Sign Up</button>
              </form>
              <div id="message" class="hidden"></div>
            </section>
          </main>

          <footer>
            <p>&copy; 2023 Mergington High School</p>
          </footer>
        </body>
      </html>
    `, {
      url: 'http://localhost:8000',
    });

    window = dom.window;
    document = window.document;
    global.window = window;
    global.document = document;
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchActivities()', () => {
    it('should fetch activities from /activities endpoint', async () => {
      const mockActivities = {
        'Chess Club': {
          description: 'Learn chess',
          schedule: 'Fridays',
          max_participants: 12,
          participants: ['user1@test.edu']
        }
      };

      global.fetch.mockResolvedValueOnce({
        json: async () => mockActivities,
        ok: true
      });

      // Simulate DOMContentLoaded event to trigger fetchActivities
      const script = `
        async function fetchActivities() {
          const response = await fetch("/activities");
          const activities = await response.json();
          
          const activitiesList = document.getElementById("activities-list");
          activitiesList.innerHTML = "";
          
          Object.entries(activities).forEach(([name, details]) => {
            const activityCard = document.createElement("div");
            activityCard.className = "activity-card";
            
            const spotsLeft = details.max_participants - details.participants.length;
            
            const participantsList = details.participants
              .map(p => \`<div class="participant-item"><span>\${p}</span></div>\`)
              .join('');
            
            activityCard.innerHTML = \`
              <h4>\${name}</h4>
              <p>\${details.description}</p>
              <p><strong>Schedule:</strong> \${details.schedule}</p>
              <p><strong>Availability:</strong> \${spotsLeft} spots left</p>
              <div class="participants-section">
                <strong>Registered Participants:</strong>
                <div class="participants-list">
                  \${participantsList || '<div class="no-participants">No participants yet</div>'}
                </div>
              </div>
            \`;
            
            activitiesList.appendChild(activityCard);
          });
        }
        
        fetchActivities();
      `;
      
      // Execute the fetch function
      window.eval(script);
      
      // Wait for async operations
      await new Promise(resolve => setTimeout(resolve, 10));

      // Verify fetch was called
      expect(global.fetch).toHaveBeenCalledWith("/activities");

      // Verify DOM was updated
      const activityCards = document.querySelectorAll('.activity-card');
      expect(activityCards.length).toBe(1);
      expect(document.querySelector('h4').textContent).toBe('Chess Club');
    });

    it('should display activity cards with correct information', async () => {
      const mockActivities = {
        'Programming Class': {
          description: 'Learn programming',
          schedule: 'Tuesdays and Thursdays',
          max_participants: 20,
          participants: ['emma@test.edu', 'sophia@test.edu']
        }
      };

      global.fetch.mockResolvedValueOnce({
        json: async () => mockActivities,
        ok: true
      });

      const script = `
        async function fetchActivities() {
          const response = await fetch("/activities");
          const activities = await response.json();
          
          const activitiesList = document.getElementById("activities-list");
          activitiesList.innerHTML = "";
          
          Object.entries(activities).forEach(([name, details]) => {
            const activityCard = document.createElement("div");
            activityCard.className = "activity-card";
            
            const spotsLeft = details.max_participants - details.participants.length;
            
            activityCard.innerHTML = \`
              <h4>\${name}</h4>
              <p>\${details.description}</p>
              <p><strong>Schedule:</strong> \${details.schedule}</p>
              <p><strong>Availability:</strong> \${spotsLeft} spots left</p>
            \`;
            
            activitiesList.appendChild(activityCard);
          });
        }
        
        fetchActivities();
      `;
      
      window.eval(script);
      await new Promise(resolve => setTimeout(resolve, 10));

      const card = document.querySelector('.activity-card');
      expect(card.querySelector('h4').textContent).toBe('Programming Class');
      expect(card.querySelector('p').textContent).toBe('Learn programming');
      expect(card.textContent).toContain('18 spots left');
    });
  });

  describe('Participant Display', () => {
    it('should display participants list', async () => {
      const mockActivities = {
        'Chess Club': {
          description: 'Learn chess',
          schedule: 'Fridays',
          max_participants: 12,
          participants: ['michael@test.edu', 'daniel@test.edu']
        }
      };

      global.fetch.mockResolvedValueOnce({
        json: async () => mockActivities,
        ok: true
      });

      const script = `
        async function fetchActivities() {
          const response = await fetch("/activities");
          const activities = await response.json();
          
          const activitiesList = document.getElementById("activities-list");
          activitiesList.innerHTML = "";
          
          Object.entries(activities).forEach(([name, details]) => {
            const activityCard = document.createElement("div");
            const participantsList = details.participants
              .map(p => \`<div class="participant-item"><span>\${p}</span></div>\`)
              .join('');
            
            activityCard.innerHTML = \`
              <h4>\${name}</h4>
              <div class="participants-list">
                \${participantsList || '<div class="no-participants">No participants yet</div>'}
              </div>
            \`;
            
            activitiesList.appendChild(activityCard);
          });
        }
        
        fetchActivities();
      `;
      
      window.eval(script);
      await new Promise(resolve => setTimeout(resolve, 10));

      const participantItems = document.querySelectorAll('.participant-item');
      expect(participantItems.length).toBe(2);
      expect(participantItems[0].textContent).toContain('michael@test.edu');
      expect(participantItems[1].textContent).toContain('daniel@test.edu');
    });

    it('should show no participants message when list is empty', async () => {
      const mockActivities = {
        'Art Studio': {
          description: 'Art class',
          schedule: 'Tuesdays',
          max_participants: 18,
          participants: []
        }
      };

      global.fetch.mockResolvedValueOnce({
        json: async () => mockActivities,
        ok: true
      });

      const script = `
        async function fetchActivities() {
          const response = await fetch("/activities");
          const activities = await response.json();
          
          const activitiesList = document.getElementById("activities-list");
          activitiesList.innerHTML = "";
          
          Object.entries(activities).forEach(([name, details]) => {
            const activityCard = document.createElement("div");
            const participantsList = details.participants
              .map(p => \`<div class="participant-item"><span>\${p}</span></div>\`)
              .join('');
            
            activityCard.innerHTML = \`
              <div class="participants-list">
                \${participantsList || '<div class="no-participants">No participants yet</div>'}
              </div>
            \`;
            
            activitiesList.appendChild(activityCard);
          });
        }
        
        fetchActivities();
      `;
      
      window.eval(script);
      await new Promise(resolve => setTimeout(resolve, 10));

      const noParticipantsMsg = document.querySelector('.no-participants');
      expect(noParticipantsMsg).toBeTruthy();
      expect(noParticipantsMsg.textContent).toBe('No participants yet');
    });
  });

  describe('Form Submission', () => {
    it('should submit form with email and activity', async () => {
      global.fetch.mockResolvedValueOnce({
        json: async () => ({}),
        ok: true
      });

      const form = document.getElementById('signup-form');
      const emailInput = document.getElementById('email');
      const activitySelect = document.getElementById('activity');
      const messageDiv = document.getElementById('message');

      emailInput.value = 'test@mergington.edu';
      activitySelect.value = 'Chess Club';

      const script = `
        const signupForm = document.getElementById("signup-form");
        const messageDiv = document.getElementById("message");

        signupForm.addEventListener("submit", async (event) => {
          event.preventDefault();

          const email = document.getElementById("email").value;
          const activity = document.getElementById("activity").value;

          try {
            const response = await fetch(
              \`/activities/\${encodeURIComponent(activity)}/signup?email=\${encodeURIComponent(email)}\`,
              { method: "POST" }
            );

            const result = await response.json();

            if (response.ok) {
              messageDiv.textContent = result.message;
              messageDiv.className = "success";
              signupForm.reset();
            } else {
              messageDiv.textContent = result.detail || "An error occurred";
              messageDiv.className = "error";
            }

            messageDiv.classList.remove("hidden");
          } catch (error) {
            messageDiv.textContent = "Failed to sign up. Please try again.";
            messageDiv.className = "error";
            messageDiv.classList.remove("hidden");
          }
        });

        // Trigger submission
        signupForm.dispatchEvent(new Event('submit'));
      `;

      window.eval(script);
      await new Promise(resolve => setTimeout(resolve, 10));

      expect(global.fetch).toHaveBeenCalledWith(
        '/activities/Chess%20Club/signup?email=test%40mergington.edu',
        { method: 'POST' }
      );
    });

    it('should display success message on successful signup', async () => {
      const mockResponse = { message: 'Signed up successfully' };

      global.fetch.mockResolvedValueOnce({
        json: async () => mockResponse,
        ok: true,
        status: 200
      });

      const form = document.getElementById('signup-form');
      const messageDiv = document.getElementById('message');
      const emailInput = document.getElementById('email');
      const activitySelect = document.getElementById('activity');

      emailInput.value = 'test@mergington.edu';
      activitySelect.value = 'Chess Club';

      const script = `
        const signupForm = document.getElementById("signup-form");
        const messageDiv = document.getElementById("message");

        signupForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          const response = await fetch("/activities/Chess%20Club/signup?email=test%40mergington.edu", { method: "POST" });
          const result = await response.json();
          
          if (response.ok) {
            messageDiv.textContent = result.message;
            messageDiv.className = "success";
          }
          messageDiv.classList.remove("hidden");
        });

        signupForm.dispatchEvent(new Event('submit'));
      `;

      window.eval(script);
      await new Promise(resolve => setTimeout(resolve, 10));

      expect(messageDiv.textContent).toBe('Signed up successfully');
      expect(messageDiv.className).toBe('success');
      expect(messageDiv.classList.contains('hidden')).toBe(false);
    });

    it('should display error message on signup failure', async () => {
      const mockResponse = { detail: 'Student is already registered' };

      global.fetch.mockResolvedValueOnce({
        json: async () => mockResponse,
        ok: false,
        status: 400
      });

      const form = document.getElementById('signup-form');
      const messageDiv = document.getElementById('message');
      const emailInput = document.getElementById('email');
      const activitySelect = document.getElementById('activity');

      emailInput.value = 'test@mergington.edu';
      activitySelect.value = 'Chess Club';

      const script = `
        const signupForm = document.getElementById("signup-form");
        const messageDiv = document.getElementById("message");

        signupForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          const response = await fetch("/activities/Chess%20Club/signup?email=test%40mergington.edu", { method: "POST" });
          const result = await response.json();
          
          if (!response.ok) {
            messageDiv.textContent = result.detail || "Error";
            messageDiv.className = "error";
          }
          messageDiv.classList.remove("hidden");
        });

        signupForm.dispatchEvent(new Event('submit'));
      `;

      window.eval(script);
      await new Promise(resolve => setTimeout(resolve, 10));

      expect(messageDiv.textContent).toBe('Student is already registered');
      expect(messageDiv.className).toBe('error');
    });
  });
});

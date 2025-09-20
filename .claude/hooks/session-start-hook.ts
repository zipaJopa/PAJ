#!/usr/bin/env bun

async function sendNotification(title: string, message: string, priority: string = 'normal') {
  try {
    const response = await fetch('http://localhost:8888/notify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title,
        message,
        voice_enabled: true,
        priority,
        voice_id: 'jqcCZkN6Knx8BJ5TBdYR'  // Kai's voice ID
      }),
    });
    
    if (!response.ok) {
      console.error(`Notification failed: ${response.status}`);
    }
  } catch (error) {
    console.error('Failed to send notification:', error);
  }
}

async function main() {
  try {
    const message = `Kai here, ready to go.`;
    await sendNotification('Kai Systems Initialized', message, 'low');
    process.exit(0);
  } catch (error) {
    console.error('SessionStart hook error:', error);
    process.exit(1);
  }
}

main();
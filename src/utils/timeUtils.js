import moment from 'moment-timezone';
import fs from 'fs';
import path from 'path';
import 'dotenv/config';

const TIMEZONE = process.env.TIMEZONE || 'America/New_York';

/**
 * @typedef {object} TimeContext
 * @property {string} currentTime - Current time in HH:MM format.
 * @property {string} currentDate - Current date in "Day, Month DD, YYYY" format.
 * @property {string} timeOfDay - "morning", "afternoon", "evening", or "night".
 * @property {string} timestamp - Current timestamp in ISO format.
 */

/**
 * Gets the current time context.
 * @returns {TimeContext} The current time context.
 */
export function getTimeContext() {
  const now = moment().tz(TIMEZONE);
  const hour = now.hour();
  let timeOfDay;

  if (hour >= 5 && hour < 12) {
    timeOfDay = "morning";
  } else if (hour >= 12 && hour < 18) {
    timeOfDay = "afternoon";
  } else if (hour >= 18 && hour < 22) {
    timeOfDay = "evening";
  } else {
    timeOfDay = "night";
  }

  return {
    currentTime: now.format("HH:mm"),
    currentDate: now.format("dddd, MMMM DD, YYYY"),
    timeOfDay: timeOfDay,
    timestamp: now.toISOString(),
  };
}

/**
 * Calculates how long ago the last chat occurred based on file modification time.
 * @param {string} sessionFilePath - Path to the session file.
 * @returns {string} A human-readable string indicating how long ago the last chat was.
 */
export function getDaysSinceLastChat(sessionFilePath) {
  if (!fs.existsSync(sessionFilePath)) {
    return "First conversation";
  }

  try {
    const stats = fs.statSync(sessionFilePath);
    const lastModified = moment(stats.mtime);
    const now = moment();
    const diffMinutes = now.diff(lastModified, 'minutes');
    const diffHours = now.diff(lastModified, 'hours');
    const diffDays = now.diff(lastModified, 'days');

    if (diffMinutes < 1) {
        return "Just now";
    } else if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
    } else if (diffDays === 1) {
      return "Yesterday";
    } else {
      return `${diffDays} days ago`;
    }
  } catch (error) {
    console.error("Error getting file stats:", error);
    return "Error determining last session";
  }
}

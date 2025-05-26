/**
 * Utility functions for fetching authenticated image data using session cookies
 */

/**
 * Fetches an image from the server using session authentication
 * @param {string} imageUrl - The relative URL of the image
 * @returns {Promise<string>} - Promise resolving to a data URL for the image
 */
export function getImageData(imageUrl) {
  const mediaUrl = import.meta.env.VITE_DJANGO_MEDIA_URL + imageUrl;
  return fetch(mediaUrl, {
    credentials: "include", // Include cookies in the request
  })
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Authentication failed");
      }
      return response.text();
    })
    .then((response) => {
      return `data:image;base64,${response}`;
    });
}

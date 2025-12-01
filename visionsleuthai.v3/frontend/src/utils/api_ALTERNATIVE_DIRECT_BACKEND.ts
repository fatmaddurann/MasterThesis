/**
 * ALTERNATIVE IMPLEMENTATION: Direct Backend Call (Seçenek A)
 * 
 * Bu dosya sadece referans için. Eğer proxy route çalışmazsa,
 * api.ts dosyasındaki sendFrame fonksiyonunu bu versiyonla değiştirebilirsiniz.
 * 
 * KULLANIM:
 * 1. api.ts dosyasındaki sendFrame fonksiyonunu bu kodla değiştir
 * 2. Backend CORS'un doğru yapılandırıldığından emin ol (zaten yapılandırılmış)
 * 3. Frontend artık doğrudan Render backend'e istek atacak
 */

export const sendFrame_DIRECT_BACKEND = async (imageData: string) => {
  try {
    // Validate input
    if (!imageData || typeof imageData !== 'string') {
      throw new Error('Invalid image data provided');
    }

    // Get backend URL from environment variable
    // In production, this should be: https://masterthesis-zk81.onrender.com
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk81.onrender.com';
    const backendUrlFull = `${backendUrl.replace(/\/+$/, '')}/api/live/frame`;

    // DEĞİŞİKLİK: Doğrudan Render backend'e istek atıyoruz (CORS gerekecek)
    const response = await fetch(backendUrlFull, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageData }),
      // Add timeout to prevent hanging requests
      signal: AbortSignal.timeout(30000), // 30 second timeout
    });

    // Handle non-OK responses with detailed error messages
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = {
          error: `Server returned ${response.status} ${response.statusText}`,
        };
      }
      
      // Provide user-friendly error messages based on status code
      if (response.status === 404) {
        throw new Error('API endpoint not found. The backend route may not be deployed.');
      } else if (response.status === 500) {
        throw new Error(errorData.error || 'Backend server error. Please try again later.');
      } else if (response.status === 504) {
        throw new Error('Request timeout. Backend may be slow or unavailable.');
      } else {
        throw new Error(errorData.error || errorData.detail || `Failed to process frame: ${response.status}`);
      }
    }

    // Parse and return successful response
    try {
      return await response.json();
    } catch (parseError) {
      throw new Error('Failed to parse backend response');
    }
  } catch (error) {
    // Re-throw with better error messages
    if (error instanceof Error) {
      // Check for timeout/abort errors
      if (error.name === 'AbortError' || error.message.includes('timeout')) {
        throw new Error('Request timeout. Backend may be slow or unavailable.');
      }
      // Check for CORS errors
      if (error.message.includes('CORS') || error.message.includes('Access-Control')) {
        throw new Error('CORS error: Backend may not be configured to allow requests from this origin.');
      }
      // Check for network errors
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        throw new Error('Network error. Please check your internet connection.');
      }
      // Re-throw with original message
      throw error;
    }
    // Unknown error
    throw new Error('Unknown error occurred while processing frame');
  }
};



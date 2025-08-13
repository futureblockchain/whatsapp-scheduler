import axios from 'axios';
import toast from 'react-hot-toast';

// Configuración base de axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.message || error.message || 'Error desconocido';
    console.error('API Error:', error);
    
    if (error.response?.status !== 404) { // No mostrar toast para 404
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

// ============================================================================
// FUNCIONES DE API
// ============================================================================

export const apiService = {
  // Verificar estado de la API
  async checkHealth() {
    const response = await api.get('/');
    return response.data;
  },

  // Crear mensaje programado
  async createScheduledMessage(messageData) {
    const response = await api.post('/api/schedule', messageData);
    return response.data;
  },

  // Obtener mensajes programados con filtros
  async getScheduledMessages(params = {}) {
    const {
      page = 1,
      per_page = 50,
      status = null,
      phone = null
    } = params;

    const queryParams = new URLSearchParams({
      page: page.toString(),
      per_page: per_page.toString(),
    });

    if (status) queryParams.append('status', status);
    if (phone) queryParams.append('phone', phone);

    const response = await api.get(`/api/scheduled?${queryParams}`);
    return response.data;
  },

  // Obtener un mensaje específico
  async getScheduledMessage(messageId) {
    const response = await api.get(`/api/scheduled/${messageId}`);
    return response.data;
  },

  // Actualizar mensaje programado
  async updateScheduledMessage(messageId, updateData) {
    const response = await api.put(`/api/scheduled/${messageId}`, updateData);
    return response.data;
  },

  // Eliminar mensaje programado
  async deleteScheduledMessage(messageId) {
    const response = await api.delete(`/api/scheduled/${messageId}`);
    return response.data;
  },

  // Enviar mensaje inmediatamente (testing)
  async sendMessageNow(messageData) {
    const response = await api.post('/api/send-now', messageData);
    return response.data;
  },

  // Obtener estadísticas del sistema
  async getStats() {
    const response = await api.get('/api/stats');
    return response.data;
  }
};

// Funciones helper para formatear datos
export const formatters = {
  // Formatear fecha para el input datetime-local
  toDateTimeLocal(date) {
    if (!date) return '';
    
    const d = new Date(date);
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 16);
  },

  // Formatear fecha para mostrar al usuario
  toDisplayDate(date) {
    if (!date) return '-';
    
    return new Date(date).toLocaleString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  // Formatear número de teléfono sin agregar prefijo automáticamente
  formatPhone(phone) {
    if (!phone) return '';
    
    // Quitar caracteres no numéricos excepto +
    let clean = phone.replace(/[^\d+]/g, '');
    
    // Asegurar que empiece con '+'
    if (!clean.startsWith('+')) {
      clean = '+' + clean;
    }
    
    return clean;
  },

  // Truncar texto largo
  truncateText(text, maxLength = 50) {
    if (!text) return '';
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  },

  // Obtener estado del mensaje para mostrar
  getMessageStatus(message) {
    if (message.is_sent) {
      return { status: 'sent', label: 'Enviado', color: 'text-green-600' };
    }
    
    if (message.error_message) {
      return { status: 'failed', label: 'Fallido', color: 'text-red-600' };
    }
    
    const now = new Date();
    const sendTime = new Date(message.send_time);
    
    if (sendTime <= now) {
      return { status: 'overdue', label: 'Atrasado', color: 'text-orange-600' };
    }
    
    return { status: 'pending', label: 'Pendiente', color: 'text-blue-600' };
  }
};

export default api;
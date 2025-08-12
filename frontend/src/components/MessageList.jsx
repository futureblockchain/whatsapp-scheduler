import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  RefreshCw,
  Phone,
  MessageSquare,
  Clock,
  Send,
  AlertTriangle
} from 'lucide-react';
import { apiService, formatters } from '../api';
import toast from 'react-hot-toast';

const MessageList = ({ onEditMessage }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalMessages, setTotalMessages] = useState(0);

  useEffect(() => {
    loadMessages();
  }, [currentPage, statusFilter]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) {
        loadMessages();
      } else {
        setCurrentPage(1);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      
      const params = {
        page: currentPage,
        per_page: 10,
        status: statusFilter === 'all' ? null : statusFilter,
        phone: searchTerm.trim() || null
      };

      const response = await apiService.getScheduledMessages(params);
      
      setMessages(response.messages);
      setTotalMessages(response.total);
      setTotalPages(Math.ceil(response.total / 10));
      
    } catch (error) {
      console.error('Error loading messages:', error);
      toast.error('Error cargando mensajes');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteMessage = async (messageId) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este mensaje?')) {
      return;
    }

    try {
      await apiService.deleteScheduledMessage(messageId);
      toast.success('Mensaje eliminado correctamente');
      loadMessages();
    } catch (error) {
      console.error('Error deleting message:', error);
      toast.error('Error eliminando mensaje');
    }
  };

  const StatusBadge = ({ message }) => {
    const status = formatters.getMessageStatus(message);
    
    const statusConfig = {
      sent: { icon: Send, bg: 'bg-green-100', text: 'text-green-700' },
      failed: { icon: AlertTriangle, bg: 'bg-red-100', text: 'text-red-700' },
      pending: { icon: Clock, bg: 'bg-blue-100', text: 'text-blue-700' },
      overdue: { icon: AlertTriangle, bg: 'bg-orange-100', text: 'text-orange-700' }
    };

    const config = statusConfig[status.status];
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        <Icon className="h-3 w-3" />
        <span>{status.label}</span>
      </span>
    );
  };

  if (loading && messages.length === 0) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mensajes Programados</h1>
          <p className="text-gray-600">
            {totalMessages} mensaje{totalMessages !== 1 ? 's' : ''} total{totalMessages !== 1 ? 'es' : ''}
          </p>
        </div>
        <button
          onClick={loadMessages}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-whatsapp-500 text-white rounded-lg hover:bg-whatsapp-600 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Actualizar</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 mb-6">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Buscar por número de teléfono..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-whatsapp-500 focus:border-transparent"
          />
        </div>

        {/* Status Filter */}
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-whatsapp-500 focus:border-transparent appearance-none bg-white"
          >
            <option value="all">Todos los estados</option>
            <option value="pending">Pendientes</option>
            <option value="sent">Enviados</option>
            <option value="failed">Fallidos</option>
          </select>
        </div>
      </div>

      {/* Messages List */}
      {messages.length > 0 ? (
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Header info */}
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="flex items-center space-x-2">
                      <Phone className="h-4 w-4 text-gray-500" />
                      <span className="font-medium text-gray-900">{message.phone}</span>
                    </div>
                    <StatusBadge message={message} />
                  </div>

                  {/* Message content */}
                  <div className="mb-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <MessageSquare className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">Mensaje:</span>
                    </div>
                    <p className="text-gray-800 bg-gray-50 p-3 rounded-lg">
                      {formatters.truncateText(message.message, 150)}
                    </p>
                  </div>

                  {/* Timing info */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-600">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4" />
                      <div>
                        <span className="font-medium">Programado:</span>
                        <br />
                        <span>{formatters.toDisplayDate(message.send_time)}</span>
                      </div>
                    </div>
                    
                    {message.sent_at && (
                      <div className="flex items-center space-x-2">
                        <Send className="h-4 w-4" />
                        <div>
                          <span className="font-medium">Enviado:</span>
                          <br />
                          <span>{formatters.toDisplayDate(message.sent_at)}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Error message */}
                  {message.error_message && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                        <span className="text-sm font-medium text-red-700">Error:</span>
                      </div>
                      <p className="text-sm text-red-600 mt-1">{message.error_message}</p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4">
                  {!message.is_sent && (
                    <button
                      onClick={() => onEditMessage(message.id)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Editar mensaje"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => handleDeleteMessage(message.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Eliminar mensaje"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No hay mensajes</h3>
          <p className="text-gray-600">
            {searchTerm || statusFilter !== 'all' 
              ? 'No se encontraron mensajes con los filtros aplicados' 
              : 'Aún no has programado ningún mensaje'
            }
          </p>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-8">
          <div className="text-sm text-gray-700">
            Mostrando {((currentPage - 1) * 10) + 1} al {Math.min(currentPage * 10, totalMessages)} de {totalMessages} mensajes
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            
            {[...Array(totalPages)].map((_, i) => {
              const page = i + 1;
              if (page === currentPage || Math.abs(page - currentPage) <= 2) {
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-2 rounded-lg text-sm ${
                      page === currentPage
                        ? 'bg-whatsapp-500 text-white'
                        : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                );
              }
              return null;
            })}
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList;
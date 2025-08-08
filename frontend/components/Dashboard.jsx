import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, 
  Send, 
  Clock, 
  AlertTriangle,
  TrendingUp,
  Calendar,
  Users,
  Activity
} from 'lucide-react';
import { apiService, formatters } from '../api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentMessages, setRecentMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Cargar estadísticas
      const statsData = await apiService.getStats();
      setStats(statsData);

      // Cargar mensajes recientes (últimos 5)
      const messagesData = await apiService.getScheduledMessages({ 
        page: 1, 
        per_page: 5 
      });
      setRecentMessages(messagesData.messages);

    } catch (error) {
      console.error('Error loading dashboard:', error);
      toast.error('Error cargando dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 h-24 rounded-lg"></div>
            ))}
          </div>
          <div className="bg-gray-200 h-64 rounded-lg"></div>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Mensajes',
      value: stats?.total_messages || 0,
      icon: MessageSquare,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600'
    },
    {
      title: 'Mensajes Enviados',
      value: stats?.sent_messages || 0,
      icon: Send,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600'
    },
    {
      title: 'Pendientes',
      value: stats?.pending_messages || 0,
      icon: Clock,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-600'
    },
    {
      title: 'Fallidos',
      value: stats?.failed_messages || 0,
      icon: AlertTriangle,
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
      textColor: 'text-red-600'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Resumen de tu sistema de mensajes</p>
        </div>
        <button
          onClick={loadDashboardData}
          className="flex items-center space-x-2 px-4 py-2 bg-whatsapp-500 text-white rounded-lg hover:bg-whatsapp-600 transition-colors"
        >
          <Activity className="h-4 w-4" />
          <span>Actualizar</span>
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.textColor}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Success Rate */}
      {stats?.total_messages > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Tasa de Éxito</h3>
              <div className="flex items-center space-x-4">
                <div className="flex-1 bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-green-500 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${stats.success_rate}%` }}
                  ></div>
                </div>
                <span className="text-2xl font-bold text-green-600">
                  {stats.success_rate}%
                </span>
              </div>
            </div>
            <TrendingUp className="h-8 w-8 text-green-500" />
          </div>
        </div>
      )}

      {/* Recent Messages */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Mensajes Recientes</h3>
        </div>
        
        {recentMessages.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {recentMessages.map((message) => {
              const status = formatters.getMessageStatus(message);
              return (
                <div key={message.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-1">
                        <span className="font-medium text-gray-900">
                          {message.phone}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${status.color} bg-opacity-10`}>
                          {status.label}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-2">
                        {formatters.truncateText(message.message, 80)}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>Programado: {formatters.toDisplayDate(message.send_time)}</span>
                        </div>
                        {message.sent_at && (
                          <div className="flex items-center space-x-1">
                            <Send className="h-3 w-3" />
                            <span>Enviado: {formatters.toDisplayDate(message.sent_at)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-6 text-center text-gray-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No hay mensajes recientes</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Send, MessageSquare, Phone, Zap, AlertTriangle } from 'lucide-react';
import { apiService, formatters } from '../api';
import toast from 'react-hot-toast';

const TestMessage = () => {
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm({
    defaultValues: {
      phone: '',
      message: ''
    }
  });

  // Watch para mostrar preview
  const watchedMessage = watch('message');
  const watchedPhone = watch('phone');

  // Función local para formatear teléfono en preview sin forzar +52
  const formatPhonePreview = (phone) => {
    if (!phone) return '';
    // Solo limpiar espacios, guiones y paréntesis
    return phone.replace(/[\s\-()]/g, '');
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      setLastResult(null);

      // Formatear los datos para enviar (usar el helper oficial)
      const messageData = {
        phone: formatters.formatPhone(data.phone), // Asumiendo que formatPhone respeta el prefijo si ya está
        message: data.message.trim()
      };

      const result = await apiService.sendMessageNow(messageData);

      setLastResult(result);

      if (result.success) {
        toast.success('Mensaje enviado exitosamente');
      } else {
        toast.error(`Error enviando mensaje: ${result.error}`);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error.response?.data?.detail || 'Error enviando el mensaje';
      toast.error(errorMessage);
      setLastResult({
        success: false,
        error: errorMessage,
        status: 'failed',
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    reset();
    setLastResult(null);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-yellow-100 rounded-lg">
            <Zap className="h-6 w-6 text-yellow-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Envío Directo</h1>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-700">Modo de Testing</span>
          </div>
          <p className="text-yellow-700 text-sm">
            Este modo envía mensajes inmediatamente sin programarlos. 
            Úsalo para probar la conexión con WhatsApp.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Número de teléfono */}
        <div>
          <label htmlFor="phone" className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
            <Phone className="h-4 w-4" />
            <span>Número de WhatsApp</span>
          </label>
          <input
            id="phone"
            type="tel"
            placeholder="+52 55 1234 5678"
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition-colors ${
              errors.phone ? 'border-red-500' : 'border-gray-300'
            }`}
            {...register('phone', {
              required: 'El número de teléfono es requerido',
              pattern: {
                // Validar formato internacional E.164 básico: + y entre 10 y 15 dígitos
                value: /^\+?[1-9]\d{9,14}$/,
                message: 'Formato inválido. Use un número internacional válido con prefijo +'
              }
            })}
          />
          {errors.phone && (
            <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
          )}
        </div>

        {/* Mensaje */}
        <div>
          <label htmlFor="message" className="flex items-center justify-between text-sm font-medium text-gray-700 mb-2">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4" />
              <span>Mensaje</span>
            </div>
            <span className="text-xs text-gray-500">
              {watchedMessage?.length || 0} / 4096 caracteres
            </span>
          </label>
          <textarea
            id="message"
            rows={5}
            placeholder="Mensaje de prueba..."
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition-colors resize-none ${
              errors.message ? 'border-red-500' : 'border-gray-300'
            }`}
            {...register('message', {
              required: 'El mensaje es requerido',
              maxLength: {
                value: 4096,
                message: 'El mensaje no puede exceder 4096 caracteres'
              },
              minLength: {
                value: 1,
                message: 'El mensaje no puede estar vacío'
              }
            })}
          />
          {errors.message && (
            <p className="mt-1 text-sm text-red-600">{errors.message.message}</p>
          )}
        </div>

        {/* Preview */}
        {(watchedPhone || watchedMessage) && (
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Vista Previa</h3>
            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-8 h-8 bg-whatsapp-500 rounded-full flex items-center justify-center">
                  <Phone className="h-4 w-4 text-white" />
                </div>
                <div>
                  <p className="font-medium text-sm text-gray-900">
                    {watchedPhone ? formatPhonePreview(watchedPhone) : 'Número no especificado'}
                  </p>
                  <p className="text-xs text-gray-500">WhatsApp</p>
                </div>
              </div>
              <div className="bg-whatsapp-50 rounded-lg p-3 ml-10">
                <p className="text-sm text-gray-800">
                  {watchedMessage || 'Tu mensaje aparecerá aquí...'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Botones */}
        <div className="flex space-x-4 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Enviando...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Enviar Ahora</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleClear}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Limpiar
          </button>
        </div>
      </form>

      {/* Resultado del último envío */}
      {lastResult && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Resultado del Envío</h3>

          <div className={`border rounded-lg p-4 ${
            lastResult.success
              ? 'bg-green-50 border-green-200'
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center space-x-2 mb-3">
              {lastResult.success ? (
                <>
                  <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                  <span className="font-medium text-green-700">Éxito</span>
                </>
              ) : (
                <>
                  <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                  <span className="font-medium text-red-700">Error</span>
                </>
              )}
            </div>

            <div className="space-y-2 text-sm">
              <div>
                <span className="font-medium text-gray-700">Estado:</span>
                <span className={`ml-2 ${
                  lastResult.success ? 'text-green-600' : 'text-red-600'
                }`}>
                  {lastResult.status}
                </span>
              </div>

              <div>
                <span className="font-medium text-gray-700">Fecha:</span>
                <span className="ml-2 text-gray-600">
                  {formatters.toDisplayDate(lastResult.timestamp)}
                </span>
              </div>

              {lastResult.message_id && (
                <div>
                  <span className="font-medium text-gray-700">ID del mensaje:</span>
                  <span className="ml-2 text-gray-600 font-mono text-xs">
                    {lastResult.message_id}
                  </span>
                </div>
              )}

              {lastResult.error && (
                <div>
                  <span className="font-medium text-gray-700">Error:</span>
                  <p className="mt-1 text-red-600">{lastResult.error}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestMessage;
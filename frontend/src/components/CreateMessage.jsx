import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { MessageSquare, Phone, Calendar, Send } from 'lucide-react';
import { apiService, formatters } from '../api';
import toast from 'react-hot-toast';

const CreateMessage = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm({
    defaultValues: {
      phone: '',
      message: '',
      send_time: ''
    }
  });

  // Watch para mostrar preview
  const watchedMessage = watch('message');
  const watchedPhone = watch('phone');

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      // Formatear los datos
      const messageData = {
        phone: formatters.formatPhone(data.phone),
        message: data.message.trim(),
        send_time: new Date(data.send_time).toISOString()
      };

      // Validar que la fecha sea en el futuro
      const sendTime = new Date(data.send_time);
      if (sendTime <= new Date()) {
        toast.error('La fecha y hora debe ser en el futuro');
        return;
      }

      await apiService.createScheduledMessage(messageData);
      
      toast.success('Mensaje programado exitosamente');
      reset();
      
      if (onSuccess) {
        onSuccess();
      }
      
    } catch (error) {
      console.error('Error creating message:', error);
      const errorMessage = error.response?.data?.detail || 'Error creando el mensaje';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Obtener fecha mínima (ahora + 1 minuto)
  const getMinDateTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 1);
    return formatters.toDateTimeLocal(now);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-whatsapp-100 rounded-lg">
            <MessageSquare className="h-6 w-6 text-whatsapp-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Programar Mensaje</h1>
        </div>
        <p className="text-gray-600">
          Programa un mensaje de WhatsApp para enviarse automáticamente
        </p>
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
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-whatsapp-500 focus:border-transparent transition-colors ${
              errors.phone ? 'border-red-500' : 'border-gray-300'
            }`}
            {...register('phone', {
              required: 'El número de teléfono es requerido',
              pattern: {
                value: /^(\+?52)?[0-9]{10}$/,
                message: 'Formato inválido. Use: +52XXXXXXXXXX o XXXXXXXXXX'
              }
            })}
          />
          {errors.phone && (
            <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            Formato: +52 seguido de 10 dígitos (ejemplo: +52 55 1234 5678)
          </p>
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
            placeholder="Escribe tu mensaje aquí..."
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-whatsapp-500 focus:border-transparent transition-colors resize-none ${
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

        {/* Fecha y hora de envío */}
        <div>
          <label htmlFor="send_time" className="flex items-center space-x-2 text-sm font-medium text-gray-700 mb-2">
            <Calendar className="h-4 w-4" />
            <span>Fecha y Hora de Envío</span>
          </label>
          <input
            id="send_time"
            type="datetime-local"
            min={getMinDateTime()}
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-whatsapp-500 focus:border-transparent transition-colors ${
              errors.send_time ? 'border-red-500' : 'border-gray-300'
            }`}
            {...register('send_time', {
              required: 'La fecha y hora es requerida',
              validate: (value) => {
                const sendTime = new Date(value);
                const now = new Date();
                if (sendTime <= now) {
                  return 'La fecha y hora debe ser en el futuro';
                }
                return true;
              }
            })}
          />
          {errors.send_time && (
            <p className="mt-1 text-sm text-red-600">{errors.send_time.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            El mensaje se enviará automáticamente en la fecha y hora especificada
          </p>
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
                    {watchedPhone ? formatters.formatPhone(watchedPhone) : 'Número no especificado'}
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
            className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-whatsapp-500 text-white rounded-lg hover:bg-whatsapp-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Programando...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Programar Mensaje</span>
              </>
            )}
          </button>
          
          <button
            type="button"
            onClick={() => reset()}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Limpiar
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateMessage;
import { Certificate } from '../types/certificate';

export const API_BASE_URL = 'http://localhost:5001';

export interface CertificateLevel {
    label: string;
    value: string;
}

interface CreateCertificateData {
    names: string;
    date: string;
    cert: string;
}

export const certificatesApi = {
    // Получение списка сертификатов
    async getCertificates(): Promise<Certificate[]> {
        const response = await fetch(`${API_BASE_URL}/certificates`);
        if (!response.ok) {
            throw new Error('Failed to fetch certificates');
        }
        return response.json();
    },

    // Получение уровней сертификатов
    getCertificateLevels: async (): Promise<CertificateLevel[]> => {
        const response = await fetch(`${API_BASE_URL}/levels`);
        if (!response.ok) {
            throw new Error('Ошибка при загрузке уровней сертификатов');
        }
        const data = await response.json();
        return data || [];
    },

    // Создание сертификатов
    async generateCertificates(data: CreateCertificateData): Promise<{ message: string; files: string[] }> {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error('Failed to generate certificates');
        }
        return response.json();
    },

    // Удаление сертификата
    async deleteCertificate(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/certificates/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new Error('Failed to delete certificate');
        }
    },

    downloadRecentCertificates: async (): Promise<void> => {
        try {
            const response = await fetch(`${API_BASE_URL}/recently`, {
                method: 'GET',
            });

            if (!response.ok) {
                throw new Error('Ошибка при скачивании сертификатов');
            }

            // Получаем имя файла из заголовка Content-Disposition
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'certificates.zip';

            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1];
                }
            }

            // Скачиваем файл
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Ошибка при скачивании сертификатов:', error);
            throw error;
        }
    },
}; 
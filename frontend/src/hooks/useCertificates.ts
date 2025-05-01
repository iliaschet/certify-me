import { useState, useCallback } from 'react';
import { Certificate } from '../types/certificate';
import { certificatesApi, CertificateLevel } from '../api/certificates';

interface CreateCertificateData {
    names: string;
    date: string;
    cert: string;
}

export function useCertificates() {
    const [certificates, setCertificates] = useState<Certificate[]>([]);
    const [certificateLevels, setCertificateLevels] = useState<CertificateLevel[]>([]);
    const [error, setError] = useState<string | undefined>();
    const [success, setSuccess] = useState<string | undefined>();
    const [isLoading, setIsLoading] = useState(false);

    const fetchCertificates = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await certificatesApi.getCertificates();
            setCertificates(data);
        } catch (e) {
            console.error(e)
            setError('Error loading certificates');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchCertificateLevels = useCallback(async () => {
        try {
            const levels = await certificatesApi.getCertificateLevels();
            setCertificateLevels(levels);
        } catch (e) {
            console.error(e)
            setError('Error loading certificate levels');
        }
    }, []);

    const createCertificate = useCallback(async (data: CreateCertificateData) => {
        setIsLoading(true);
        try {
            await certificatesApi.generateCertificates(data);
            setSuccess('Certificates successfully created');
            setError(undefined);
            await fetchCertificates();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
            setSuccess(undefined);
        } finally {
            setIsLoading(false);
        }
    }, [fetchCertificates]);

    const deleteCertificate = useCallback(async (id: string) => {
        if (!window.confirm('Are you sure you want to delete this certificate?')) {
            return;
        }

        setIsLoading(true);
        try {
            await certificatesApi.deleteCertificate(id);
            setSuccess('Certificate successfully removed');
            setError(undefined);
            await fetchCertificates();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
            setSuccess(undefined);
        } finally {
            setIsLoading(false);
        }
    }, [fetchCertificates]);

    const clearMessages = useCallback(() => {
        setError(undefined);
        setSuccess(undefined);
    }, []);

    return {
        certificates,
        certificateLevels,
        error,
        success,
        isLoading,
        fetchCertificates,
        fetchCertificateLevels,
        createCertificate,
        deleteCertificate,
        clearMessages
    };
} 
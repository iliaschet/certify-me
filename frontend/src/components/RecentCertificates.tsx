import { useEffect, useState } from 'react';
import { certificatesApi } from '../api/certificates';
import type { Certificate } from '../types/certificate';
import { Button, Alert } from '@mui/material';

interface RecentCertificatesProps {
    certificates: Certificate[];
}

export const RecentCertificates = ({ certificates }: RecentCertificatesProps) => {
    const [hasCertificates, setHasCertificates] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [latestDate, setLatestDate] = useState<string | null>(null);

    useEffect(() => {
        const checkCertificates = async () => {
            try {
                setHasCertificates(certificates.length > 0);

                if (certificates.length > 0) {
                    // Find the latest date
                    const sortedCertificates = [...certificates].sort((a, b) => {
                        return new Date(b.addedAt).getTime() - new Date(a.addedAt).getTime();
                    });

                    const latestCertificate = sortedCertificates[0];
                    setLatestDate(latestCertificate.addedAt);
                }
            } catch (error) {
                console.error('Error checking certificates:', error);
            }
        };

        checkCertificates();
    }, [certificates]);

    const handleDownload = async () => {
        try {
            setIsLoading(true);
            await certificatesApi.downloadRecentCertificates();
        } catch (error) {
            console.error('Error downloading certificates:', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (!hasCertificates) {
        return null;
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <Alert icon={false} severity="success" action={
            <Button
                color="success"
                onClick={handleDownload}
                disabled={isLoading}
                variant="contained"
                size="small"
            >
                Download
            </Button>
        }>
            The last group of certificates from {latestDate ? formatDate(latestDate) : 'unknown'}
        </Alert>
    );
};
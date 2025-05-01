import { API_BASE_URL } from '../api/certificates';
import type { Certificate } from '../types/certificate';
import { useState, useEffect } from 'react';
import {MRT_ColumnDef, MaterialReactTable, MRT_ActionMenuItem, MRT_RowData} from 'material-react-table';
import { RecentCertificates } from './RecentCertificates';
import { PictureAsPdf, Delete } from '@mui/icons-material';
import { Box, Container } from '@mui/material';
import { useCertificates } from './../hooks/useCertificates'
import { CertificateForm } from './CertificateForm';
import { useSnackbar } from 'notistack';
import moment from "moment";

export function CertificateList() {
    const [deletingId, setDeletingId] = useState<string | null>(null);
    const { enqueueSnackbar } = useSnackbar();

    const {
        certificates,
        certificateLevels,
        deleteCertificate,
        isLoading,
        createCertificate,
        fetchCertificates,
        fetchCertificateLevels,
        error,
        success,
    } = useCertificates();

    useEffect(() => {
        fetchCertificates();
        fetchCertificateLevels();
    }, [fetchCertificates, fetchCertificateLevels]);

    useEffect(() => {
        if (error) {
            enqueueSnackbar(error, { variant: 'error' });
        }
        if (success) {
            enqueueSnackbar(success, { variant: 'success' });
        }
    }, [enqueueSnackbar, error, success]);

    const columns: MRT_ColumnDef<Certificate>[] = [
        {
            accessorKey: 'fullName',
            header: 'Name',
            size: 650,
        },
        {
            accessorKey: 'date',
            header: 'Date',
            size: 100,
            Cell: ({ cell }) => (
                cell.getValue<string>() ? moment(cell.getValue<string>()).format("DD.MM.YYYY") : ''
            ),
        },
        {
            accessorKey: 'addedAt',
            header: 'Added',
            size: 200,
            // filterVariant: 'date',
            // sortingFn: 'datetime',
            Cell: ({ cell }) => (
                cell.getValue<string>() ? new Date(cell.getValue<string>()).toLocaleString() : ''
            ),
        }
    ];

    const handleDelete = async (cert: MRT_RowData) => {
        try {
            setDeletingId(cert.id);
            await deleteCertificate(cert.id);
        } catch (error) {
            console.error('Error deleting certificate:', error);
        } finally {
            setDeletingId(null);
        }
    };

    const handleSubmit = async (data: { names: string; date: string; cert: string }) => {
        await createCertificate(data);
    };

    return (
        <Container maxWidth="lg" sx={{ marginTop: '20px' }}>
            <Box className="w-full rounded-lg border border-gray-200 overflow-hidden bg-white shadow-sm">
                <MaterialReactTable
                    columns={columns}
                    data={certificates}
                    enableRowActions
                    positionActionsColumn='last'
                    renderRowActionMenuItems={({ row, table }) => [
                        <MRT_ActionMenuItem
                            icon={<PictureAsPdf />}
                            key="pdf"
                            label="Download PDF"
                            onClick={() => window.open(`${API_BASE_URL}/certificates/${row.original.id}.pdf`, '_blank')}
                            table={table}
                        />,
                        <MRT_ActionMenuItem
                            icon={<Delete />}
                            key="delete"
                            label="Delete"
                            disabled={deletingId === row.original.id}
                            onClick={() => handleDelete(row.original)}
                            table={table}
                        />,
                    ]}
                    renderTopToolbarCustomActions={() => (
                        <Box sx={{ display: 'flex', gap: '1rem', p: '4px' }}>
                            <CertificateForm
                                onSubmit={handleSubmit}
                                isLoading={isLoading}
                                certificateLevels={certificateLevels}
                            />
                            <RecentCertificates certificates={certificates} />
                        </Box>
                    )}
                    initialState={{
                        sorting: [{ id: 'addedAt', desc: true }]
                    }}
                />
            </Box>
        </Container>
    );
} 
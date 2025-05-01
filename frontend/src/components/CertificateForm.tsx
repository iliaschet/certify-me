import { useState, FormEvent, ChangeEvent, useEffect } from 'react';
import { Button, Dialog, DialogTitle, DialogContent, DialogContentText, Box, TextField, FormControl, InputLabel, Select, MenuItem, OutlinedInput } from '@mui/material';
import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import 'dayjs/locale/ru';
import dayjs from 'dayjs';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};


interface CertificateFormProps {
    onSubmit: (data: { names: string; date: string; cert: string }) => Promise<void>;
    isLoading: boolean;
    certificateLevels: { value: string; label: string; }[];
}

export function CertificateForm({ onSubmit, isLoading, certificateLevels }: CertificateFormProps) {
    const [open, setOpen] = useState(false);
    const [names, setNames] = useState('');
    const [date, setDate] = useState(dayjs());
    const [certificateLevel, setCertificateLevel] = useState(certificateLevels[0]?.value || '');


    useEffect(() => {
        setCertificateLevel(certificateLevels[0]?.value || '');
    }, [certificateLevels])

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        console.log('Email:', names, 'Password: ', names);


        if (!names.trim() || !date || !certificateLevel) return;

        await onSubmit({
            names: names.trim(),
            date: date.toISOString(),
            cert: certificateLevel
        });

        setNames('');
        setDate(dayjs());
        setCertificateLevel(certificateLevels[0]?.value || '');
        setOpen(false);
    };

    const handleNameChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setNames(e.target.value);
    };


    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    return (
        <>
            <Button color="primary" variant="contained" onClick={handleClickOpen}>
                Add certificates
            </Button>
            <Dialog
                fullWidth
                maxWidth="lg"
                open={open}
                onClose={handleClose}
                aria-labelledby="certificate-dialog-title"
                disableEnforceFocus
                disableAutoFocus
                keepMounted={false}
            >
                <DialogTitle id="certificate-dialog-title">Creating certificates</DialogTitle>
                <DialogContent>
                    <DialogContentText sx={{ mb: 2 }}>Enter a list of full names, separated by commas and/or line breaks. Each full name must be within 32 characters.</DialogContentText>
                    <Box
                        noValidate
                        component="form"
                        onSubmit={handleSubmit}
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 4,
                            maxWidth: '100%'
                        }}
                    >
                        <TextField
                            label="List of full names"
                            multiline
                            fullWidth
                            rows={5}
                            value={names}
                            onChange={handleNameChange}
                            placeholder={`Ivanov Ivan Ivanovich, Petrov Petr Petrovich
Smirnov Alexander Alexandrovich`}
                            required
                        />

                        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="en">
                            <DemoContainer components={['DatePicker']}>
                                <DatePicker
                                    label="Date of issue of certificates"
                                    value={date}
                                    onChange={(newValue) => setDate(newValue || dayjs())}
                                />
                            </DemoContainer>
                        </LocalizationProvider>

                        <FormControl fullWidth>
                            <InputLabel id="demo-multiple-name-label">Certificate level</InputLabel>
                            <Select
                                labelId="demo-multiple-name-label"
                                id="demo-multiple-name"
                                value={certificateLevel}
                                onChange={(e) => setCertificateLevel(e.target.value as string)}
                                input={<OutlinedInput label="Certificate level" />}
                                MenuProps={MenuProps}
                            >
                                {certificateLevels.map((level) => (
                                    <MenuItem key={level.value} value={level.value}>
                                        {level.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                            <Button color="primary" variant="text" onClick={handleClose}>
                                Cancel
                            </Button>
                            <Button
                                color="primary"
                                variant="contained"
                                type="submit"
                                disabled={isLoading}
                            >
                                {isLoading ? 'Generation...' : 'Generate'}
                            </Button>
                        </Box>
                    </Box>
                </DialogContent>
            </Dialog>
        </>
    );
} 
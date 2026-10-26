import React from 'react';
import ApiUnavailable from '../../../components/ApiUnavailable';

const Page = ({ isHidden = false }) => <div className={isHidden ? 'hidden' : ''}><ApiUnavailable title="Thông báo kho" detail="Management API hiện chưa có endpoint thông báo." /></div>;

export default Page;

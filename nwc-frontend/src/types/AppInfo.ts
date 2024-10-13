export interface AppInfo {
  clientId: string;
  name: string;
  nip05Verified: boolean;
  domain: string;
  avatar: string;
  nip68Verification?: {
    status: string;
    authorityName: string;
    authorityPubKey: string;
  } | null;
}

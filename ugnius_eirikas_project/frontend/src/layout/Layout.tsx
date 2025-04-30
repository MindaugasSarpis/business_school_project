import Header from "./Header"

export const Layout = ({children}: {children: React.ReactNode}) => {
    return (
        <>
       <Header/>
        <div className="mx-auto max-w-screen-xl px-4 py-2 lg:px-8 lg:py-4 min-h-100vh container">
        {children}
        </div>
        </>
    )
}